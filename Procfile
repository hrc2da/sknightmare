web: gunicorn --worker-class eventlet -w 4 sknightmare.flask_app:app
worker: celery -A sknightmare.flask_app.celery worker
