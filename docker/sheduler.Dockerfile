FROM python:3.9-alpine

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./scheduler/requirements.txt .
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt


COPY ./scheduler ./scheduler
