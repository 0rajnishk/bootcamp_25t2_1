from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS



app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"


api = Api(app)
db = SQLAlchemy(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False) #admin, manager, employee
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

with app.app_context():
    db.create_all()

class HelloWorld(Resource):
    def get(self):
        return 'hello world'
    
    def post(self):
        data = request.get_json()
        name = data['username']
        return 'hello ' + name

class SignupResource(Resource):
    def post(self):
        data = request.get_json()
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data['role']
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_json(), 201
    

api.add_resource(HelloWorld, '/api/')
api.add_resource(SignupResource, '/api/signup')

if __name__ == '__main__':
    app.run()