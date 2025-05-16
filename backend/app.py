from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["JWT_SECRET_KEY"] = "aStrongSecretKey"  # Change this!
jwt = JWTManager(app)

api = Api(app)
db = SQLAlchemy(app)

CORS(app, resources={r"/*": {"origins": "*"}})

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee') #admin, manager, employee
    is_approved = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_approved': self.is_approved
        }


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False) #open, in progress, closed
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id
        }


class HelloWorld(Resource):
    
    def get(self):
        return {"msg":'get from hello world'}
    
    @jwt_required()
    def post(self):
        user_name = get_jwt_identity()
        return 'hello ' + user_name

class SignupResource(Resource):
    def post(self):
        data = request.get_json()
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            # role=data['role']
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_json(), 201
    
class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email'], password=data['password']).first()

        if user:
            access_token=create_access_token(identity=user.username)
            print(access_token)

            return {'token':access_token, 'message':'successfully logged in'}, 200
        else:
            return {'message': 'Invalid credentials'}, 401

class AdminResource(Resource):
    
    def get(self):
        users = User.query.filter_by(is_approved=False).all()
        J_users = []
        for user in users:
            user_details = {'user_id': user.id, 'username': user.username, 'email': user.email}
            J_users.append(user_details)
        return jsonify(J_users)

    # @jwt_required()
    def post(self):
        data = request.json
        
        user_id = data['user_id']
        user = User.query.get(user_id)
        if user:
            user.is_approved = True
            db.session.commit()
 

        return "post from admin resource"

api.add_resource(HelloWorld, '/')
api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(AdminResource, '/admin')


def create_admin():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@mail.com',
                password='admin@123',
                role='admin',
                is_approved=True
            )
            db.session.add(admin)
            db.session.commit()


if __name__ == '__main__':
    create_admin()
    app.run()