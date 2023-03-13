#!/bin/sh

cd /usr/src/notification_api/utils
python wait_for_raddit.py
cd /usr/src/notification_api
uvicorn main:app --host 0.0.0.0 --port 8010 --access-log