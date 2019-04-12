FROM ubuntu:latest
MAINTAINER Nikhil Dhawan "nd353@cornell.edu"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
RUN apt-get install -y git
RUN apt-get install -y redis
# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8000




