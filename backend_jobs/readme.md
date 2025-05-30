# install redis
sudo apt update
sudo apt install redis-server

# Start Redis
sudo systemctl start redis

# Check Redis status
sudo systemctl status redis

# Start the Flask app
python3 main.py

# Start Celery Worker
celery -A main.celery worker --loglevel=info

# Start Celery Beat
celery -A main.celery beat --loglevel=info