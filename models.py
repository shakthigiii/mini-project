# models.py
from app import db
from flask_login import UserMixin 
import json


class Student(db.Model, UserMixin):
    __tablename__ = 'students' # Explicitly set table name to avoid conflicts
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    batch = db.Column(db.String(50), nullable=False)
    role = 'student' # Hardcode the role for this table

    def get_id(self):
        return str(self.id)

class Faculty(db.Model, UserMixin):
    __tablename__ = 'faculties'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = 'faculty'

    def get_id(self):
        return str(self.id)
    
class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = 'admin'

    def get_id(self):
        return str(self.id)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    students = db.relationship('ClassStudent', backref='class_obj')

class ClassStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    student = db.relationship('Student', backref='class_links')

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id')) # Updated foreign key
    duration_minutes = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    # Corrected relationship definition to use the association object
    questions = db.relationship('QuizQuestion', backref='quiz')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_option_index = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    # Corrected relationship definition
    quizzes = db.relationship('QuizQuestion', backref='question')

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

class QuizAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id')) # Updated foreign key
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    student = db.relationship('Student', backref='quiz_results')
    quiz = db.relationship('Quiz', backref='results')