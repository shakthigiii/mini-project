# Change Password Route (for students and teachers)
# routes.py
from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from models import *
import io
import pandas as pd
import csv
import openpyxl
import random
import json
@app.route('/faculty/download_quiz_excel/<int:quiz_id>')
@login_required
def download_quiz_excel(quiz_id):
    if not isinstance(current_user, Faculty):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)
    # Get all classes assigned to this quiz
    assigned_classes = db.session.query(Class).join(QuizAssignment, QuizAssignment.class_id == Class.id).filter(QuizAssignment.quiz_id == quiz.id).all()

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default sheet

    for class_obj in assigned_classes:
        ws = wb.create_sheet(title=class_obj.name)
        # Students who attended
        results = QuizResult.query.filter_by(quiz_id=quiz.id).join(Student).join(ClassStudent, ClassStudent.student_id == Student.id).filter(ClassStudent.class_id == class_obj.id).order_by(Student.username).all()
        ws.append(["Attended Students", "Score (%)"])
        for result in results:
            ws.append([result.student.username, round(result.score, 2)])

        ws.append([])
        # Students who did not attend
        students_who_took_quiz = [result.student.id for result in results]
        assigned_students = db.session.query(Student).join(ClassStudent, ClassStudent.student_id == Student.id).filter(ClassStudent.class_id == class_obj.id).all()
        non_attenders = [s for s in assigned_students if s.id not in students_who_took_quiz]
        ws.append(["Students Who Did Not Attend"])
        for student in non_attenders:
            ws.append([student.username])

    # Save to BytesIO and send as file
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f"quiz_{quiz.id}_results.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from models import *
import random
import json

# --- Auth Routes ---
@app.route('/')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# FIX: The login route now redirects to the home page (the new index.html)
# if there is an authentication failure.
@app.route('/login/<role_name>', methods=['POST'])
def login(role_name):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    username = request.form['username']
    password = request.form['password']
    user = None
    
    if role_name == 'student':
        user = Student.query.filter_by(username=username).first()
    elif role_name == 'faculty':
        user = Faculty.query.filter_by(username=username).first()
    elif role_name == 'admin':
        user = Admin.query.filter_by(username=username).first()
    else:
        flash('Invalid login request.', 'danger')
        return redirect(url_for('login_page'))
    
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        session['user_role'] = user.role
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Login Unsuccessful. Please check your credentials.', 'danger')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_page'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = current_user
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not bcrypt.check_password_hash(user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('change_password.html')
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('change_password.html')
        if len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'danger')
            return render_template('change_password.html')

        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('change_password.html')
@app.route('/dashboard')
@login_required
def dashboard():
    if isinstance(current_user, Student):
        return redirect(url_for('student_dashboard'))
    elif isinstance(current_user, Faculty):
        return redirect(url_for('faculty_dashboard'))
    elif isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid role', 'danger')
        logout_user()
        return redirect(url_for('login_page'))
    

# --- Student Routes ---
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if not isinstance(current_user, Student):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    student = current_user
    # Fetches quizzes assigned to the student's class
    assigned_quizzes = Quiz.query.join(QuizAssignment).join(Class).join(ClassStudent).filter(ClassStudent.student_id == student.id).all()

    # FIX: Ensure this line renders the new template name
    return render_template('Student_portal.html', quizzes=assigned_quizzes)

@app.route('/student/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    if not isinstance(current_user, Student):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if the student has already submitted this quiz
    result = QuizResult.query.filter_by(student_id=current_user.id, quiz_id=quiz.id).first()
    if result:
        flash('You have already completed this quiz.', 'info')
        return redirect(url_for('student_dashboard'))

    session['quiz_start_flag'] = True 

    return render_template('Start_Exam_Page.html', quiz=quiz)

@app.route('/student/quiz_start/<int:quiz_id>')
@login_required
def start_actual_quiz(quiz_id):
    if not isinstance(current_user, Student):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check for existing submission to prevent re-entry
    result = QuizResult.query.filter_by(student_id=current_user.id, quiz_id=quiz_id).first()
    if result:
        flash('You have already completed this quiz.', 'info')
        return redirect(url_for('student_dashboard'))
    
    # The rest of your logic to get questions and randomize them
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.join(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    random.shuffle(questions)

    shuffled_questions = []
    for q in questions:
        options = json.loads(q.options)
        random.shuffle(options)
        shuffled_q = {
            'id': q.id,
            'question_text': q.question_text,
            'options': options,
            'subject': q.subject
        }
        shuffled_questions.append(shuffled_q)
# Pass the flag to the quiz page, then clear it
    start_flag = session.pop('quiz_start_flag', False)
    
    # Pass the flag to the template
    return render_template('quiz.html', quiz=quiz, questions=shuffled_questions, start_flag=start_flag)

@app.route('/student/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    if not isinstance(current_user, Student):
        return jsonify({'message': 'Access Denied'}), 403

    quiz = Quiz.query.get_or_404(quiz_id)
    student = current_user
    answers = request.form

    score = 0
    total_questions = 0

    questions = Question.query.join(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    
    for question in questions:
        total_questions += 1
        submitted_answer_text = answers.get(f'question_{question.id}')

        if submitted_answer_text:
            options = json.loads(question.options)
            correct_option_text = options[question.correct_option_index]

            if submitted_answer_text == correct_option_text:
                score += 1
    
    final_score_percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    new_result = QuizResult(
        student_id=student.id,
        quiz_id=quiz.id,
        score=final_score_percentage
    )
    db.session.add(new_result)
    db.session.commit()

    flash(f'Quiz submitted successfully. Your score is {score}/{total_questions} ({final_score_percentage:.2f}%)', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/student/scores')
@login_required
def view_scores():
    if not isinstance(current_user, Student):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    student = current_user
    all_results = QuizResult.query.filter_by(student_id=student.id).all()
    
    results_with_titles = db.session.query(QuizResult, Quiz).join(Quiz).filter(QuizResult.student_id == student.id).all()

    return render_template('student_scores.html', results=results_with_titles)

# --- Faculty Routes ---
@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    if not isinstance(current_user, Faculty):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Logic to fetch quizzes created by this faculty
    my_quizzes = Quiz.query.filter_by(faculty_id=current_user.id).all()
    
    # Render the new Manage Exams page
    return render_template('manage_exams.html', my_quizzes=my_quizzes)

# Update create_quiz to render a form page for creating a quiz
@app.route('/faculty/create_quiz', methods=['GET'])
@login_required
def create_quiz_form():
    if not isinstance(current_user, Faculty):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Renders the provided combined form (which contains metadata and question adding)
    return render_template('create_quiz_form.html')

# FIX: You need to rename the old POST route to 'create_quiz_process'
# and link it to the form's action.
@app.route('/faculty/create_quiz_process', methods=['POST'])
@login_required
def create_quiz_process():
    if not isinstance(current_user, Faculty):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    # 1. Get Exam Metadata and Questions (from the single combined form)
    title = request.form.get('title')
    duration = request.form.get('duration')
    subject = request.form.get('subject')
    questions_json = request.form.get('questions_json') # This field comes from the JavaScript

    # Basic Validation
    if not title or not duration or not subject or not questions_json:
        flash('Missing exam details or questions. Please add at least one question.', 'danger')
        return redirect(url_for('create_quiz_form'))

    # 2. Create the Quiz Record
    faculty = current_user
    new_quiz = Quiz(title=title, duration_minutes=duration, faculty_id=faculty.id, subject=subject)
    db.session.add(new_quiz)
    db.session.flush() # Use flush to get the new_quiz.id before committing

    # 3. Process Questions
    questions_data = json.loads(questions_json)
    
    if not questions_data:
        flash('Quiz created, but no questions were found in the data.', 'warning')
        db.session.commit()
        return redirect(url_for('faculty_dashboard'))

    for q_data in questions_data:
        # a) Create the new Question record
        new_question = Question(
            question_text=q_data['description'],
            options=json.dumps(q_data['options']),
            correct_option_index=q_data['correct_index'],
            subject=subject
        )
        db.session.add(new_question)
        db.session.flush()

        # b) Link the question to the quiz
        quiz_question_link = QuizQuestion(quiz_id=new_quiz.id, question_id=new_question.id)
        db.session.add(quiz_question_link)

    db.session.commit()
    flash(f'Quiz "{title}" created successfully with {len(questions_data)} questions!', 'success')
    return redirect(url_for('faculty_dashboard'))

@app.route('/faculty/add_questions/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_questions(quiz_id):
    if not isinstance(current_user, Faculty):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        # (Your existing POST logic to link questions to the quiz)
        question_ids = request.form.getlist('question_ids')
        
        # NOTE: This POST logic needs to be careful. It should probably remove unchecked questions too, 
        # but for simplicity, we'll assume it only adds new selections here.
        
        for q_id in question_ids:
            existing_link = QuizQuestion.query.filter_by(quiz_id=quiz.id, question_id=q_id).first()
            if not existing_link:
                link = QuizQuestion(quiz_id=quiz.id, question_id=q_id)
                db.session.add(link)
        
        db.session.commit()
        flash('Questions added successfully!', 'success')
        return redirect(url_for('faculty_dashboard'))

    # --- GET REQUEST LOGIC (New Grouping and Filtering) ---
    all_questions = Question.query.all()
    
    # Get a list of IDs of questions already assigned to this quiz
    assigned_q_ids = db.session.query(QuizQuestion.question_id).filter(QuizQuestion.quiz_id == quiz_id).all()
    assigned_q_ids = {q[0] for q in assigned_q_ids}
    
    questions_by_subject = {}
    
    for q in all_questions:
        subject = q.subject
        # Attach a flag indicating if the question is already in the quiz
        q_data = {
            'id': q.id,
            'question_text': q.question_text,
            'is_assigned': q.id in assigned_q_ids
            # Add other data if needed
        }
        
        if subject not in questions_by_subject:
            questions_by_subject[subject] = []
        
        questions_by_subject[subject].append(q_data)

    # FIX: Pass the grouped data to the template
    return render_template('add_questions.html', quiz=quiz, questions_by_subject=questions_by_subject)
@app.route('/faculty/create_question', methods=['GET', 'POST'])
@login_required
def create_question():
    if not isinstance(current_user, Faculty):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        question_text = request.form.get('question_text')
        options = request.form.getlist('options')
        correct_index = request.form.get('correct_option_index')
        subject = request.form.get('subject')

        if not all(options) or correct_index is None:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('create_question'))

        new_question = Question(
            question_text=question_text,
            options=json.dumps(options),
            correct_option_index=int(correct_index),
            subject=subject
        )
        db.session.add(new_question)
        db.session.commit()
        flash('Question created successfully!', 'success')
        return redirect(url_for('faculty_dashboard'))
    
    return render_template('create_question.html')

@app.route('/faculty/assign_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def assign_quiz(quiz_id):
    if not isinstance(current_user, Faculty):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        class_id = request.form.get('class_id')
        if not class_id:
            flash('Please select a class.', 'danger')
            return redirect(url_for('assign_quiz', quiz_id=quiz_id))

        existing_assignment = QuizAssignment.query.filter_by(quiz_id=quiz.id, class_id=class_id).first()
        if existing_assignment:
            flash('This quiz has already been assigned to this class.', 'info')
        else:
            new_assignment = QuizAssignment(quiz_id=quiz.id, class_id=class_id)
            db.session.add(new_assignment)
            db.session.commit()
            flash(f'Quiz "{quiz.title}" assigned successfully!', 'success')
        
        return redirect(url_for('faculty_dashboard'))

    all_classes = Class.query.all()
    return render_template('assign_quiz.html', quiz=quiz, classes=all_classes)

@app.route('/faculty/view_quiz_results/<int:quiz_id>')
@login_required
def view_quiz_results(quiz_id):
    if not isinstance(current_user, Faculty):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    results = QuizResult.query.filter_by(quiz_id=quiz.id).join(Student).order_by(Student.username).all()
    students_who_took_quiz = [result.student.id for result in results]
    assigned_students = db.session.query(Student).join(ClassStudent, ClassStudent.student_id == Student.id).join(Class, ClassStudent.class_id == Class.id).join(QuizAssignment, QuizAssignment.class_id == Class.id).filter(QuizAssignment.quiz_id == quiz.id).all()
    non_attenders = [s for s in assigned_students if s.id not in students_who_took_quiz]

    return render_template('view_quiz_results.html', quiz=quiz, results=results, non_attenders=non_attenders)

# --- Admin Routes ---
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    all_students = Student.query.all()
    all_faculties = Faculty.query.all()
    all_classes = Class.query.all()

    return render_template('admin_dashboard.html', 
                           students=all_students, 
                           faculties=all_faculties, 
                           classes=all_classes)

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    # ... (existing logic for single user/faculty addition) ...
    if not isinstance(current_user, Admin):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        batch = request.form.get('batch') # Used only for student

        # --- User Existence Check (Consolidated) ---
        Model = {'student': Student, 'faculty': Faculty}.get(role)
        if Model:
            existing_user = Model.query.filter_by(username=username).first()
            if existing_user:
                flash(f'{role.capitalize()} username already exists.', 'danger')
                return redirect(url_for('add_user'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # --- Create User ---
        if role == 'student':
            new_user = Student(username=username, password_hash=hashed_password, batch=batch)
        elif role == 'faculty':
            new_user = Faculty(username=username, password_hash=hashed_password)
        else:
            flash('Invalid role specified.', 'danger')
            return redirect(url_for('add_user'))

        db.session.add(new_user)
        db.session.commit()
        
        flash(f'{role.capitalize()} added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_user.html')

# NEW ROUTE: Handles bulk CSV upload and student creation
@app.route('/admin/add_batch_students', methods=['POST'])
@login_required
def add_batch_students():
    if not isinstance(current_user, Admin):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    batch_name = request.form.get('batch_name')
    csv_file = request.files.get('csv_file')
    
    if not batch_name or not csv_file:
        flash('Missing batch name or file.', 'danger')
        return redirect(url_for('add_user'))

    filename = csv_file.filename
    
    # 1. Read File using Pandas
    try:
        # Use pandas to read both CSV and XLSX formats
        if filename.endswith('.csv'):
            # Read CSV directly
            df = pd.read_csv(csv_file.stream)
        elif filename.endswith(('.xlsx', '.xls')):
            # Read Excel using openpyxl engine
            # We must save the file temporarily for pandas to read the binary Excel stream reliably
            df = pd.read_excel(csv_file.stream, engine='openpyxl')
        else:
            flash('Invalid file format. Must be CSV or XLSX.', 'danger')
            return redirect(url_for('add_user'))

        # Standardize column name lookup for PRN
        # We try to find the 'PRN' column, converting names to uppercase for robustness
        prn_column = next((col for col in df.columns if 'PRN' in col.upper()), None)
        
        if not prn_column:
            raise ValueError("CSV/Excel file must contain a column named 'PRN'.")

        # 2. Process DataFrame Rows
        new_students = []
        students_added_count = 0
        
        for index, row in df.iterrows():
            prn = str(row[prn_column]).strip()
            
            if not prn or prn.lower() == 'nan': continue # Skip empty or invalid PRNs

            existing_student = Student.query.filter_by(username=prn).first()
            if existing_student:
                continue 
            
            username = prn
            password = prn 
            
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            new_student = Student(
                username=username,
                password_hash=hashed_password,
                batch=batch_name
            )
            new_students.append(new_student)
            students_added_count += 1

        # 3. Bulk Insert into Database
        if new_students:
            db.session.add_all(new_students)
            db.session.commit()
            flash(f'Successfully added {students_added_count} students to batch {batch_name}.', 'success')
        else:
            flash('No new students found in the file or all already exist.', 'info')

    except ValueError as ve:
        flash(f'File Error: {str(ve)}', 'danger')
        return redirect(url_for('add_user'))
    except Exception as e:
        db.session.rollback()
        flash(f'An unexpected error occurred during file processing: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_class', methods=['GET', 'POST'])
@login_required
def create_class():
    if not isinstance(current_user, Admin):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # This part handles the inline form submission from admin_dashboard.html
        class_name = request.form.get('class_name')
        
        # ... (rest of the logic remains correct) ...
        existing_class = Class.query.filter_by(name=class_name).first()
        if existing_class:
            flash('Class with this name already exists.', 'danger')
            return redirect(url_for('admin_dashboard')) # Redirect back to dashboard

        new_class = Class(name=class_name)
        db.session.add(new_class)
        db.session.commit()
        flash('Class created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Since the form is now inline, this GET route should redirect to the dashboard
    # to prevent showing a blank page, but you can keep it as is if you prefer
    # a dedicated form page. Assuming you want the form on the dashboard:
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_students_to_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
def add_students_to_class(class_id):
    if not isinstance(current_user, Admin):
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))

    class_obj = Class.query.get_or_404(class_id)
    
    if request.method == 'POST':
        student_ids = request.form.getlist('student_ids')
        for s_id in student_ids:
            existing_link = ClassStudent.query.filter_by(class_id=class_obj.id, student_id=s_id).first()
            if not existing_link:
                link = ClassStudent(class_id=class_obj.id, student_id=s_id)
                db.session.add(link)
        
        db.session.commit()
        flash('Students added to class successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    all_students = Student.query.all()
    students_in_class = [cs.student_id for cs in ClassStudent.query.filter_by(class_id=class_id).all()]
    
    return render_template('add_students_to_class.html', 
                           class_obj=class_obj, 
                           students=all_students,
                           students_in_class=students_in_class)