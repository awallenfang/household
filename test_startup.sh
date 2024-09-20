#!/bin/bash

echo "Running test docker file"

echo "Building migrations"
python ./manage.py makemigrations

echo "Applying migrations"
python ./manage.py migrate

echo "Running tests"
python manage.py test

# echo "Creating superuser"
# python manage.py createsuperuser --noinput

# echo "Starting Django application"
# python manage.py runserver 0.0.0.0:42069