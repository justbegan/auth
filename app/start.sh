#!/bin/sh

set -e

sleep 10

python manage.py migrate
python manage.py collectstatic --noinput

exec uvicorn main_app.asgi:application --host 0.0.0.0 --port 8000 --workers 4 --timeout-keep-alive 120