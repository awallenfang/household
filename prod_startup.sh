#! /bin/bash

echo "Building migrations"
python ./manage.py makemigrations

echo "Applying migrations"
python ./manage.py migrate

echo "Creating superuser"
python manage.py createsuperuser --noinput

echo "Running uwsgi server"
python manage.py runserver 0.0.0.0:5000
# uwsgi --ini ./docker/uwsgi.ini