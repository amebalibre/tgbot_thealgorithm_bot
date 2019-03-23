FROM tiangolo/uwsgi-nginx-flask:python3.7-alpine3.7
MAINTAINER Ameba Libre "amebalibre@mailbox.org"

WORKDIR /app
COPY ./server /app

RUN pip3.7 install pipenv && pipenv lock && pipenv install --system
