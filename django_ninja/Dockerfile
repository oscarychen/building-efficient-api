FROM python:3.12.0-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./django_ninja/requirements.txt /usr/src/app/requirements.txt
RUN apt-get update && apt-get install -y postgresql-client && pip install -r requirements.txt
