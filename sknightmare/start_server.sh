#! /usr/bin/bash

gunicorn --worker-class eventlet -w 4 flask_app:app -b 0.0.0.0:5000
celery -A flask_app.celery worker