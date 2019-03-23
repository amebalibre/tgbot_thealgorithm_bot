FROM python:3-alpine3.7
MAINTAINER Ameba Libre "amebalibre@mailbox.org"

WORKDIR /app

COPY ./bot /app

RUN apk add -U gcc musl-dev libffi-dev openssl-dev && pip3.7 install pipenv && pipenv lock && pipenv install --system

CMD [ "python", "./main.py" ]
