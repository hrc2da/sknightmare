FROM ubuntu:18.04
COPY ./sknightmare /app/sknightmare
COPY setup.py /app/
COPY requirements.txt /app/
RUN apt update
RUN apt install -y python3-pip
RUN apt install -y redis-server
RUN python3 -m pip install -r /app/requirements.txt
RUN python3 -m pip install -e /app/
EXPOSE 5000
CMD cd /app/sknightmare && gunicorn --worker-class eventlet -w 4 flask_app:app -b 0.0.0.0:5000