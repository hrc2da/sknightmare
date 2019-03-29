web: gunicorn --worker-class eventlet -w 4 sknightmare.flask_app:app -b 0.0.0.0:5000
worker: celery -A sknightmare.flask_app.celery worker
