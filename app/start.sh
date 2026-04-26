#!/bin/sh

sleep 10

python manage.py migrate
python manage.py collectstatic --noinput

exec gunicorn main_app.wsgi:application --bind 0.0.0.0:8000 --workers 5 --timeout 300