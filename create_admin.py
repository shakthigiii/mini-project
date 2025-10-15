# create_admin.py
import sys
from getpass import getpass
from app import app, db, bcrypt # Import bcrypt here
from models import Admin

def create_admin_user():
    with app.app_context():
        # (Your existing code to create tables and check for existing admin)
        print("Creating the first admin user.")
        username = input("Enter admin username: ")
        password = getpass("Enter admin password: ")
        confirm_password = getpass("Confirm admin password: ")

        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            sys.exit()

        if not username or not password:
            print("Username and password cannot be empty.")
            sys.exit()

        # Use bcrypt.generate_password_hash to generate a compatible hash
        # The hash generated here will work with bcrypt.check_password_hash
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create and save the new user to the database
        new_admin = Admin(username=username, password_hash=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        print(f"Admin user '{username},  {hashed_password}' created successfully!")

if __name__ == '__main__':
    create_admin_user()