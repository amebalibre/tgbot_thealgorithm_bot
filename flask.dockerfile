FROM tiangolo/uwsgi-nginx-flask:python3.7
MAINTAINER Ameba Libre "amebalibre@mailbox.org"

COPY ./server /app

RUN apt-get update && apt-get upgrade -y && \
    curl --silent https://bootstrap.pypa.io/get-pip.py | python && \
    pip install -U pip && pip install pipenv && \
    pipenv install --system
