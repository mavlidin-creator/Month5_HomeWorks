#!/bin/sh

echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn main.wsgi:application --bind 0.0.0.0:8000 --workers 4
