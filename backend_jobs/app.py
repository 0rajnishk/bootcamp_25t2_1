
import os
from flask import Flask, request
from flask_restful import Api, Resource
from flask_mail import Mail, Message
from celery import Celery
import redis
from dotenv import load_dotenv
from celery.schedules import crontab
from flask_caching import Cache
cache = None
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
# Celery Configuration (Updated)
# ==========================
app.config['broker_url'] = os.getenv('BROKER_URL', 'redis://localhost:6379/0')
app.config['result_backend'] = os.getenv('RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(app.name, broker=app.config['broker_url'], backend=app.config['result_backend'])
celery.conf.broker_connection_retry_on_startup = True  # Fix Celery 6.0 deprecation warning


# ==========================
# Redis Cache Setup
# ==========================
cache = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# cache = Cache()

# cache.init_app(app)

# ==========================
# Celery Initialization
# ==========================
def init_celery(flask_app):
    celery_app = Celery(
        flask_app.import_name,
        broker=flask_app.config['broker_url'],
        backend=flask_app.config['result_backend']
    )
    celery_app.conf.update(flask_app.config)
    celery_app.conf.broker_connection_retry_on_startup = True  # Ensure retry on startup

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app

celery = init_celery(app)

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

class CacheDemo(Resource):
    # @cache.cached(timeout=60)
    def get(self):
        try:
            cached_data = cache.get('data')
            if cached_data:
                return {'data': cached_data}, 200
            else:
                data = 'This is a cached response!'
                cache.set('data', data, ex=60)
                return {'data': "set the data to cache"}, 200
        except Exception as e:
            return {'message': f"Redis Error: {str(e)}"}, 500

class DeleteCache(Resource):
    def post(self):
        try:
            cache.delete('data')
            return {'message': 'Cache deleted successfully!'}, 200
        except Exception as e:
            return {'message': f"Redis Error: {str(e)}"}, 500

@celery.task(name="tasks.background_task")
def background_task():
    return 'Task completed'

class QueuedTask(Resource):
    def get(self):
        task = background_task.apply_async()
        return {'task_id': task.id}, 202

# ==========================
# Celery Beat Configuration
# ==========================
celery.conf.timezone = 'Asia/Kolkata'
celery.conf.beat_schedule = {
    'send_reminders': {
        'task': 'tasks.send_reminders',
        'schedule': crontab(minute='*'),  # Runs daily at 7:00 AM IST
        'args': ()
    },
}

@celery.task(name="tasks.send_reminders")
def send_reminders():
    print("Reminder sent at 7:00 AM IST!")
    return "Reminder sent successfully!"

# Register API routes
api.add_resource(SendEmail, '/send-email')
api.add_resource(CacheDemo, '/cache')
api.add_resource(DeleteCache, '/delete-cache')
api.add_resource(QueuedTask, '/queued-task')

if __name__ == '__main__':
    app.run(debug=True)
