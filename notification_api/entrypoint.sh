#!/bin/sh

cd /usr/src/notification_api/utils
python wait_for_raddit.py
cd /usr/src/notification_api
gunicorn -k uvicorn.workers.UvicornWorker --bind "0.0.0.0:8010" main:app