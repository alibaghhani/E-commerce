#!/bin/sh

python /app/manage.py migrate
python /app/manage.py collectstatic
gunicorn --bind 0.0.0.0:8001 config.wsgi:application