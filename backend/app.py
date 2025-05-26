from datetime import datetime
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash

# Create a Flask web application
app = Flask(__name__)

# Configure the database to use SQLite and name the file 'project.db'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# Set a secret key for JWT (JSON Web Token) for security
app.config["JWT_SECRET_KEY"] = "aStrongSecretKey"
# Initialize JWTManager to handle JWT operations
jwt = JWTManager(app)

# Initialize Flask-RESTful API for easy creation of REST APIs
api = Api(app)
# Initialize SQLAlchemy for database operations
db = SQLAlchemy(app)

# Enable Cross-Origin Resource Sharing (CORS) for all routes
# This allows requests from different domains to access your API
CORS(app, resources={r"/*": {"origins": "*"}})

# Define the User model for the database
class User(db.Model):
    # Unique ID for each user
    id = db.Column(db.Integer, primary_key=True)
    # User's username, must be unique and cannot be empty
    username = db.Column(db.String(80), unique=True, nullable=False)
    # User's email, must be unique and cannot be empty
    email = db.Column(db.String(120), unique=True, nullable=False)
    # User's password, cannot be empty
    password = db.Column(db.String(120), nullable=False)
    # User's role (admin, manager, or employee), defaults to 'employee'
    role = db.Column(db.String(20), nullable=False, default='employee')
    # Whether the user is approved by an admin, defaults to False
    is_approved = db.Column(db.Boolean, default=False)

    # Convert user object to a JSON-friendly dictionary
    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_approved': self.is_approved
        }

# Define the Task model for the database
class Task(db.Model):
    # Unique ID for each task
    id = db.Column(db.Integer, primary_key=True)
    # Task title, cannot be empty
    title = db.Column(db.String(80), nullable=False)
    # Task description, cannot be empty
    description = db.Column(db.String(200), nullable=False)
    # Task status (open, in progress, closed), cannot be empty
    status = db.Column(db.String(20), nullable=False)
    # Deadline for the task, cannot be empty
    deadline = db.Column(db.DateTime, nullable=False)
    # When the task was created, cannot be empty
    created_at = db.Column(db.DateTime, nullable=False)
    # ID of the user assigned to this task, links to the User table
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Convert task object to a JSON-friendly dictionary
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M:%S'), # Format deadline for JSON
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') # Format creation time for JSON
        }

# Helper function to get the current logged-in user
def get_current_user():
    # Get the username from the JWT token
    username = get_jwt_identity()
    # Find the user in the database by username
    user = User.query.filter_by(username=username).first()
    return user

# Decorator to restrict access based on user roles
def role_required(allowed_roles=["admin"]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get the current user
            user = get_current_user()
            # If user is not found, return an error
            if user is None:
                return {"message": "User not found"}, 401
            # If the user's role is not in the allowed roles, return an error
            if user.role not in allowed_roles:
                return {"message": "Unauthorized access"}, 403
            # If role is allowed, execute the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Resource for a simple hello world endpoint
class HelloWorld(Resource):
    # Handle GET requests
    def get(self):
        return {"msg":'get from hello world'}
    
    # Handle POST requests, requires JWT authentication
    @jwt_required()
    def post(self):
        # Get the identity (username) from the JWT token
        user_name = get_jwt_identity()
        return {'message': 'Hello ' + user_name}

# Resource for user signup
class SignupResource(Resource):
    # Handle POST requests to create a new user
    def post(self):
        # Get user data from the request body
        data = request.get_json()
        file = request.files['file']
        # Create a new User object
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role=data['role'] # Role is set to default 'employee' upon signup
        )
        # Add the new user to the database session
        db.session.add(new_user)
        # Save changes to the database
        db.session.commit()
        # Return the new user's details as JSON with a 201 Created status
        return new_user.to_json(), 201
    
# Resource for user login
class LoginResource(Resource):
    # Handle POST requests for user login
    def post(self):
        # Get login credentials from the request body
        data = request.get_json()
        # Find the user in the database by email and password
        user = User.query.filter_by(email=data['email']).first()
        if not check_password_hash(user.password, data['password']):
            return {'message': 'Invalid credentials'}, 401

        # If user exists and is approved, create an access token
        if user and user.is_approved:
            access_token = create_access_token(identity=user.username)
            return {
                'token': access_token,
                'message': 'Successfully logged in',
                'role': user.role # <--- ADD THIS LINE
            }, 200
        elif user and not user.is_approved:
            return {'message': 'Account not approved by admin. Please wait for approval.'}, 403
        else:
            # If user not found or credentials invalid
            return {'message': 'Invalid credentials'}, 401
        
    # Handle GET requests, requires JWT authentication
    @jwt_required()
    def get(self):
        return {"message":'success'}, 200


class AllUsersResource(Resource):
    # Handle GET requests to retrieve all users
    @jwt_required()
    @role_required(['admin', 'manager'])  # Only admin can view all users
    def get(self):
        users = User.query.all()  # Get all users from the database
        all_users = []
        # Convert user objects to a list of JSON-friendly dictionaries
        for user in users:
            user_details = {'user_id': user.id, 'username': user.username, 'email': user.email, 'role': user.role}
            all_users.append(user_details)
        return jsonify(all_users)


# Resource for managing users (mainly for admin)
class UsersResource(Resource):
    # Handle GET requests to see unapproved users
    @jwt_required()
    @role_required(['admin'])
    def get(self):
        # Get all users who are not yet approved
        users = User.query.filter_by(is_approved=False).all()
        all_users = []
        # Convert user objects to a list of JSON-friendly dictionaries
        for user in users:
            user_details = {'user_id': user.id, 'username': user.username, 'email': user.email, 'role': user.role}
            all_users.append(user_details)
        return jsonify(all_users)

    # Handle POST requests to approve a user
    @jwt_required()
    @role_required(['admin'])
    def post(self):
        # Get user ID from the request body
        data = request.json
        user_id = data['user_id']
        # Find the user by ID
        user = User.query.get(user_id)
        # If user exists, approve them and save changes
        if user:
            user.is_approved = True
            db.session.commit()
            return {"msg": "Successfully approved the user"}, 200
        # If user not found
        return {"msg": "User not found"}, 404
    
    # Handle PUT requests to update user role
    @jwt_required()
    @role_required(['admin'])
    def put(self):
        data = request.json
        user_id = data.get('user_id')
        new_role = data.get('role')

        if not user_id or not new_role:
            return {"msg": "User ID and new role are required"}, 400

        user = User.query.get(user_id)
        if not user:
            return {"msg": "User not found"}, 404
        
        # Ensure the new role is valid
        if new_role not in ['admin', 'manager', 'employee']:
            return {"msg": "Invalid role specified. Must be 'admin', 'manager', or 'employee'."}, 400

        user.role = new_role
        db.session.commit()
        return {"msg": f"User {user.username} role updated to {new_role} successfully"}, 200


    # Handle DELETE requests to delete a user
    @jwt_required()
    @role_required(['admin'])
    def delete(self):
        # Get user ID from the request body
        data = request.json
        user_id = data['user_id']
        # Find the user by ID
        user = User.query.get(user_id)
        # If user not found, return an error
        if not user:
            return {"msg": "User not found"}, 404
        # Delete the user and save changes
        db.session.delete(user)
        db.session.commit()
        return {"msg":"User deleted successfully"}, 200

# Resource for managing tasks
class TaskResource(Resource):
    # Handle GET requests to retrieve tasks
    @jwt_required()
    @role_required(["admin", "manager", "employee"]) # All roles can view tasks
    def get(self, task_id=None):
        current_user = get_current_user()

        if current_user.role == 'employee':
            # Employee can only see their own tasks
            if task_id:
                task = Task.query.filter_by(id=task_id, assigned_user_id=current_user.id).first()
                if not task:
                    return {"message": "Task not found or not assigned to you"}, 404
                return task.to_json()
            else:
                tasks = Task.query.filter_by(assigned_user_id=current_user.id).all()
                all_tasks = [task.to_json() for task in tasks]
                return all_tasks
        else: # Admin and Manager can see all tasks or specific tasks
            if task_id:
                task = Task.query.get(task_id)
                if not task:
                    return {"message": "Task not found"}, 404
                return task.to_json()
            
            tasks = Task.query.all()
            all_tasks = [task.to_json() for task in tasks]
            return all_tasks
    
    # Handle POST requests to create a new task
    @jwt_required()
    @role_required(["admin", "manager"]) # Only admin and manager can create tasks
    def post(self):
        # Get task data from the request body
        data = request.json
        title = data['title']
        description = data['description']
        status = data['status']
        assigned_user_id = data['assigned_user_id']
        deadline = data['deadline']
        # Convert deadline string to datetime object
        deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')

        # Create a new Task object
        task = Task(
            title=title,
            description=description,
            status=status,
            assigned_user_id=assigned_user_id,
            deadline=deadline,
            created_at=datetime.now()
        )
        # Add the new task to the database session
        db.session.add(task)
        # Save changes to the database
        db.session.commit()
        return {"msg": "Task created successfully"}, 201

    # Handle PUT requests to update a task
    @jwt_required()
    @role_required(["admin", "manager", "employee"]) # All roles can update tasks, but with restrictions
    def put(self, task_id):
        current_user = get_current_user()
        task = Task.query.get(task_id)

        if not task:
            return {"message": "Task not found"}, 404

        data = request.json

        if current_user.role == 'employee':
            # Employee can only update status of their assigned tasks
            if task.assigned_user_id != current_user.id:
                return {"message": "You can only update tasks assigned to you"}, 403
            
            if 'status' in data:
                task.status = data['status']
            else:
                return {"message": "Employees can only update task status"}, 400
        else: # Admin and Manager can update all fields
            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'status' in data:
                task.status = data['status']
            if 'assigned_user_id' in data:
                task.assigned_user_id = data['assigned_user_id']
            if 'deadline' in data:
                task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
        
        db.session.commit()
        return {"msg": "Task updated successfully"}, 200

    # Handle DELETE requests to delete a task
    @jwt_required()
    @role_required(["admin", "manager"]) # Only admin and manager can delete tasks
    def delete(self, task_id):
        # Find the task by ID
        task = Task.query.get(task_id)
        # If task not found, return an error
        if not task:
            return {"msg": "Task not found"}, 404
        # Delete the task and save changes
        db.session.delete(task)
        db.session.commit()
        return {"msg": "Task deleted successfully"}, 200


# Add API resources to specific URLs
api.add_resource(HelloWorld, '/') # Home endpoint
api.add_resource(SignupResource, '/signup') # User signup endpoint
api.add_resource(LoginResource, '/login') # User login endpoint
api.add_resource(UsersResource,'/admin/users', '/admin/users/<int:user_id>') # Admin user management endpoint
api.add_resource(TaskResource, '/task', '/task/<int:task_id>') # Task management endpoint
api.add_resource(AllUsersResource, '/all_users') # Endpoint to get all users (for admin and manager)
# Function to create an initial admin user if one doesn't exist

def create_admin():
    # Ensure operations run within the Flask application context
    with app.app_context():
        # Create all database tables defined in the models
        db.create_all()
        # Check if an admin user already exists
        admin = User.query.filter_by(role='admin').first()
        # If no admin user found, create one
        if not admin:
            admin = User(
                username='admin',
                email='admin@mail.com',
                password=generate_password_hash('admin@123'),
                role='admin',
                is_approved=True # Admin user is automatically approved
            )
            # Add the admin user to the database session
            db.session.add(admin)
            # Save changes to the database
            db.session.commit()
            print("Default admin user created.")


# Run the Flask application
if __name__ == '__main__':
    # Create the default admin user when the application starts
    create_admin()
    # Run the app in debug mode (good for development, set to False in production)
    app.run(debug=True)