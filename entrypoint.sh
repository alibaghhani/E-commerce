#!/bin/sh

python /app/manage.py migrate

if [ ! -d "/path/to/static/root" ] || [ -z "$(ls -A /path/to/static/root)" ]; then
    echo "Static files not found, collecting static files..."
    python /app/manage.py collectstatic --noinput
else
    echo "Static files already collected."
fi

gunicorn --bind 0.0.0.0:8001 config.wsgi:application