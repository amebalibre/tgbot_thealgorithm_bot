FROM python:3
MAINTAINER Ameba Libre "amebalibre@mailbox.org"

RUN mkdir /app

WORKDIR /app

COPY ./bot /app

RUN apt-get update && apt-get upgrade -y && \
    curl --silent https://bootstrap.pypa.io/get-pip.py | python && \
    pip install -U pip && pip install pipenv && \
    pipenv install --system

CMD [ "python", "./main.py" ]
