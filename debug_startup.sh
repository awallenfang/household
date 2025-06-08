#!/bin/bash

echo "Running debug build"

echo "Building migrations"
python ./manage.py makemigrations

echo "Applying migrations"
python ./manage.py migrate

echo "Creating superuser"
python manage.py createsuperuser --noinput

python manage.py sass /code/hub/static/hub/scss /code/hub/static/hub/css -t compressed
python manage.py sass /code/todos/static/todos/scss /code/todos/static/todos/css -t compressed
python manage.py sass /code/space/static/space/scss /code/space/static/space/css -t compressed

echo "Running celery"
celery -A root worker --loglevel=info -c 4 &
echo "Running celery beat"
celery -A root beat --loglevel=info  &

echo "Starting Django application"
python manage.py runserver 0.0.0.0:5000