Let's make your Flask app more organized and use .env for your secret keys, making it easier to manage configurations and more secure.

Here's how to modularize your Flask application, keeping it simple and beginner-friendly:

Modular Flask App Structure
We'll create a structured project with separate files for configuration, models, and API routes.

your_project_name/
├── .env                  # Environment variables for secrets
├── app.py                # Main application file
├── config.py             # Configuration settings
├── models.py             # Database models (User, Task)
├── routes/               # Directory for API routes
│   ├── __init__.py       # Makes 'routes' a Python package
│   ├── auth.py           # Authentication routes (signup, login, hello world)
│   ├── admin.py          # Admin-specific routes (user management)
│   └── tasks.py          # Task-related routes
└── utils/                # Directory for helper functions
    ├── __init__.py
    └── decorators.py     # Custom decorators (role_required, get_current_user)
Step-by-Step Implementation
1. Install python-dotenv
First, if you haven't already, install the python-dotenv package:

Bash

pip install python-dotenv
2. Create .env file
In the root of your project directory (at the same level as app.py), create a file named .env and add your secret key:

Code snippet

JWT_SECRET_KEY="your_super_secret_jwt_key_here"
DATABASE_URI="sqlite:///project.db"
Note: Replace "your_super_secret_jwt_key_here" with a strong, unique secret key.

3. config.py (Configuration)
Create a file named config.py in your project root:

Python

# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    # Get JWT secret key from environment variables, essential for security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    # Get database URI from environment variables
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    # Disable SQLAlchemy event system to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
4. models.py (Database Models)
Create a file named models.py in your project root. This will hold your User and Task database models.

Python

# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy, but don't bind it to an app yet
db = SQLAlchemy()

class User(db.Model):
    """User model for storing user account information."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # Role of the user: 'admin', 'manager', or 'employee'
    role = db.Column(db.String(20), nullable=False, default='employee')
    # Indicates if the user account has been approved by an admin
    is_approved = db.Column(db.Boolean, default=False)

    def to_json(self):
        """Converts a User object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_approved': self.is_approved
        }

class Task(db.Model):
    """Task model for storing task details."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    # Status of the task: 'open', 'in progress', or 'closed'
    status = db.Column(db.String(20), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # Foreign key linking to the User who is assigned this task
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_json(self):
        """Converts a Task object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
5. utils/decorators.py (Helper Functions and Decorators)
Create a utils folder, an empty __init__.py inside it, and then decorators.py inside utils. This file will contain your helper functions like get_current_user and the role_required decorator.

Python

# utils/decorators.py
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import db, User # Import db and User from models

def get_current_user():
    """Retrieves the current logged-in user based on JWT identity."""
    # Get the username from the JWT token
    username = get_jwt_identity()
    # Query the database to find the user
    user = User.query.filter_by(username=username).first()
    return user

def role_required(allowed_roles=None):
    """
    Decorator to restrict access to API endpoints based on user roles.

    Args:
        allowed_roles (list): A list of roles that are allowed to access the endpoint.
                              Defaults to None, which will make it an empty list.
    """
    if allowed_roles is None:
        allowed_roles = [] # Ensure it's an empty list if not provided

    def decorator(func):
        # Applies JWT authentication before checking roles
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = get_current_user()
            # If user is not found (e.g., token invalid), return unauthorized
            if user is None:
                return jsonify({"message": "User not found or token invalid"}), 401
            # If user's role is not in the allowed roles, return forbidden
            if user.role not in allowed_roles:
                return jsonify({"message": "Unauthorized access: Insufficient role"}), 403
            # If all checks pass, execute the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator
6. routes/ (API Endpoints)
Create a routes folder, an empty __init__.py inside it. Then create the following files:

routes/auth.py
Python

# routes/auth.py
from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required
from models import db, User
from utils.decorators import get_current_user

class HelloWorld(Resource):
    """Simple endpoint to test the API."""
    def get(self):
        return {"msg": 'Welcome to the Task Management API!'}
    
    @jwt_required()
    def post(self):
        user_name = get_current_user().username
        return {'message': 'Hello ' + user_name + '!'}

class SignupResource(Resource):
    """Resource for user registration."""
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        # Default role is 'employee', admin approval is required
        role = data.get('role', 'employee') 

        if not username or not email or not password:
            return jsonify({"message": "Username, email, and password are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already registered"}), 409

        new_user = User(
            username=username,
            email=email,
            password=password, # In a real app, hash this password!
            role=role,
            is_approved=False # New users require admin approval
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_json(), 201
    
class LoginResource(Resource):
    """Resource for user login and token generation."""
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            # Check if the user is approved before logging in
            if not user.is_approved:
                return jsonify({'message': 'Account not approved by admin. Please wait for approval.'}), 403

            access_token = create_access_token(identity=user.username)
            return {
                'token': access_token,
                'message': 'Successfully logged in',
                'role': user.role
            }, 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
routes/admin.py
Python

# routes/admin.py
from flask import jsonify, request
from flask_restful import Resource
from models import db, User
from utils.decorators import role_required

class AdminUserManagementResource(Resource):
    """Resource for admins to manage user accounts (approve, delete, change role)."""
    
    @role_required(['admin'])
    def get(self):
        """
        Retrieves all unapproved users.
        An admin can see who needs to be approved.
        """
        users = User.query.filter_by(is_approved=False).all()
        return jsonify([user.to_json() for user in users])

    @role_required(['admin'])
    def post(self):
        """Approves a user account."""
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"msg": "User ID is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        if user.is_approved:
            return jsonify({"msg": "User is already approved"}), 400

        user.is_approved = True
        db.session.commit()
        return jsonify({"msg": f"User {user.username} approved successfully"}), 200
    
    @role_required(['admin'])
    def put(self):
        """Updates a user's role."""
        data = request.get_json()
        user_id = data.get('user_id')
        new_role = data.get('role')

        if not user_id or not new_role:
            return jsonify({"msg": "User ID and new role are required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        if new_role not in ['admin', 'manager', 'employee']:
            return jsonify({"msg": "Invalid role specified. Must be 'admin', 'manager', or 'employee'."}), 400

        user.role = new_role
        db.session.commit()
        return jsonify({"msg": f"User {user.username} role updated to {new_role} successfully"}), 200

    @role_required(['admin'])
    def delete(self):
        """Deletes a user account."""
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"msg": "User ID is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted successfully"}), 200

class AllUsersResource(Resource):
    """Resource for admins/managers to view all users."""
    @role_required(['admin', 'manager'])
    def get(self):
        """Retrieves all users from the database."""
        users = User.query.all()
        return jsonify([user.to_json() for user in users])
routes/tasks.py
Python

# routes/tasks.py
from flask import jsonify, request
from flask_restful import Resource
from datetime import datetime
from models import db, Task, User # Import User to check assigned_user_id
from utils.decorators import get_current_user, role_required

class TaskResource(Resource):
    """Resource for managing tasks (CRUD operations)."""

    @role_required(["admin", "manager", "employee"])
    def get(self, task_id=None):
        """
        Retrieves tasks.
        Admins/Managers see all tasks. Employees see only their assigned tasks.
        """
        current_user = get_current_user()

        if current_user.role == 'employee':
            if task_id:
                # Employee can only view their specific assigned task
                task = Task.query.filter_by(id=task_id, assigned_user_id=current_user.id).first()
                if not task:
                    return jsonify({"message": "Task not found or not assigned to you"}), 404
                return jsonify(task.to_json())
            else:
                # Employee can view all tasks assigned to them
                tasks = Task.query.filter_by(assigned_user_id=current_user.id).all()
                return jsonify([task.to_json() for task in tasks])
        else: # Admin and Manager roles
            if task_id:
                # Admin/Manager can view any specific task
                task = Task.query.get(task_id)
                if not task:
                    return jsonify({"message": "Task not found"}), 404
                return jsonify(task.to_json())
            else:
                # Admin/Manager can view all tasks
                tasks = Task.query.all()
                return jsonify([task.to_json() for task in tasks])
    
    @role_required(["admin", "manager"])
    def post(self):
        """Creates a new task."""
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        status = data.get('status', 'open') # Default status is 'open'
        assigned_user_id = data.get('assigned_user_id')
        deadline_str = data.get('deadline')

        if not all([title, description, assigned_user_id, deadline_str]):
            return jsonify({"message": "Missing required task fields (title, description, assigned_user_id, deadline)"}), 400
        
        # Check if the assigned user exists and is approved
        assigned_user = User.query.get(assigned_user_id)
        if not assigned_user:
            return jsonify({"message": "Assigned user does not exist"}), 404
        if not assigned_user.is_approved:
            return jsonify({"message": "Cannot assign task to an unapproved user"}), 400

        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({"message": "Invalid deadline format. Use YYYY-MM-DD HH:MM:SS"}), 400

        new_task = Task(
            title=title,
            description=description,
            status=status,
            assigned_user_id=assigned_user_id,
            deadline=deadline,
            created_at=datetime.now()
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"msg": "Task created successfully", "task": new_task.to_json()}), 201

    @role_required(["admin", "manager", "employee"])
    def put(self, task_id):
        """Updates an existing task."""
        current_user = get_current_user()
        task = Task.query.get(task_id)

        if not task:
            return jsonify({"message": "Task not found"}), 404

        data = request.get_json()

        if current_user.role == 'employee':
            # Employee can only update status of their assigned tasks
            if task.assigned_user_id != current_user.id:
                return jsonify({"message": "You can only update tasks assigned to you"}), 403
            
            if 'status' in data:
                task.status = data['status']
            else:
                return jsonify({"message": "Employees can only update task status"}), 400
        else: # Admin and Manager can update all fields
            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'status' in data:
                task.status = data['status']
            if 'assigned_user_id' in data:
                assigned_user_id = data['assigned_user_id']
                assigned_user = User.query.get(assigned_user_id)
                if not assigned_user:
                    return jsonify({"message": "Cannot assign to non-existent user"}), 404
                if not assigned_user.is_approved:
                    return jsonify({"message": "Cannot assign task to an unapproved user"}), 400
                task.assigned_user_id = assigned_user_id

            if 'deadline' in data:
                try:
                    task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return jsonify({"message": "Invalid deadline format. Use YYYY-MM-DD HH:MM:SS"}), 400
        
        db.session.commit()
        return jsonify({"msg": "Task updated successfully", "task": task.to_json()}), 200

    @role_required(["admin", "manager"])
    def delete(self, task_id):
        """Deletes a task."""
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"msg": "Task not found"}), 404
        
        db.session.delete(task)
        db.session.commit()
        return jsonify({"msg": "Task deleted successfully"}), 200
7. app.py (Main Application)
Finally, update your app.py to bring all the modular pieces together.

Python

# app.py
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from config import Config # Import Config class
from models import db, User # Import db and User model
from routes.auth import HelloWorld, SignupResource, LoginResource
from routes.admin import AdminUserManagementResource, AllUsersResource
from routes.tasks import TaskResource

def create_app():
    """Factory function to create and configure the Flask application."""
    app = Flask(__name__)
    # Load configuration from Config object
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app) # Bind SQLAlchemy to the app
    jwt = JWTManager(app) # Initialize JWT Manager
    api = Api(app) # Initialize Flask-RESTful API
    CORS(app, resources={r"/*": {"origins": "*"}}) # Enable CORS

    # Register API resources
    api.add_resource(HelloWorld, '/')
    api.add_resource(SignupResource, '/signup')
    api.add_resource(LoginResource, '/login')
    
    # Admin routes
    api.add_resource(AdminUserManagementResource, '/admin/users', '/admin/users/<int:user_id>')
    api.add_resource(AllUsersResource, '/all_users') # New endpoint to get all users

    # Task routes
    api.add_resource(TaskResource, '/task', '/task/<int:task_id>')

    return app, db # Return app and db for convenience

def create_admin_user(app, db):
    """Creates a default admin user if one doesn't exist."""
    with app.app_context():
        # Create all database tables based on models
        db.create_all()
        # Check if an admin user already exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            # Create the default admin user
            admin = User(
                username='admin',
                email='admin@mail.com',
                password='admin@123', # In a real app, hash this password!
                role='admin',
                is_approved=True # Admin is automatically approved
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created.")
        else:
            print("Admin user already exists.")


if __name__ == '__main__':
    app, db_instance = create_app() # Get both app and db instance
    create_admin_user(app, db_instance) # Pass app and db to create_admin_user
    app.run(debug=True) # Run the Flask app in debug mode
How to Run This Modular App:
Save all files in the structure described.
Ensure .env exists in your root directory with the specified variables.
Run the application from your project root:
Bash

python app.py
This modular setup improves the readability, maintainability, and scalability of your Flask application by separating different concerns into their own files and using environment variables for sensitive data.