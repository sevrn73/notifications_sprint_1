FROM python:3.9-alpine

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
USER root
RUN apk update && \
    apk add build-base librdkafka-dev && \
    apk --no-cache add curl && \
    pip install --upgrade pip && \
    pip install -U setuptools


COPY ./notification_api/requirements.txt .
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

EXPOSE 8010

COPY ./notification_api ./notification_api
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/notification_api"
RUN chmod +x /usr/src/notification_api/entrypoint.sh
ENTRYPOINT ["/usr/src/notification_api/entrypoint.sh"]
