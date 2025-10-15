# app.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta
from flask import Flask, session, request, g, jsonify
from datetime import datetime
from functools import wraps
# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_super_secret_key'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:274222@localhost/quiz_app1' # Update with your Postgre info
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'


@login_manager.user_loader
def load_user(user_id):
    from models import Student, Faculty, Admin
    # FIX: Use the role stored in the session to query the correct table
    user_role = session.get('user_role')
    
    if user_role == 'student':
        return Student.query.get(int(user_id))
    elif user_role == 'faculty':
        return Faculty.query.get(int(user_id))
    elif user_role == 'admin':
        return Admin.query.get(int(user_id))
    
    return None

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=2)

@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.before_request
def before_request():
    # Make the session permanent for the session lifetime to be enforced
    session.permanent = True
    # If the user is authenticated, update the session cookie with each request
    # This resets the inactivity timer
    if current_user.is_authenticated:
        session.modified = True
# Now, import your routes. This must be the last step.
from routes import *


if __name__ == '__main__':
    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()
    app.run(debug=True)