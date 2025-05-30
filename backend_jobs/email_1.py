from flask import Flask, jsonify, request, send_from_directory

import os
# from flask import Flask, request
from flask_restful import Api, Resource
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
api = Api(app)



# ==========================
# Flask-Mail Configuration
# ==========================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USER')

mail = Mail(app)



# ==========================
# API Routes
# ==========================
class SendEmail(Resource):
    def get(self):
        email = request.args.get('email')
        if not email:
            return {'message': 'Error: No email provided'}, 400

        msg = Message(
            subject="Test Email from Flask",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
            body="This is a test email sent via Flask and SMTP."
        )
        try:
            mail.send(msg)
            return {'message': f'Email sent successfully to {email}!'}, 200
        except Exception as e:
            return {'message': f"Error: {str(e)}"}, 500
        
        
# Register API routes
api.add_resource(SendEmail, '/send-email')


if __name__ == '__main__':
    app.run(debug=True)
