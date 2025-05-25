#! /bin/bash
python manage.py migrate
python manage.py createsuperuser --username $DJANGO_SUPERUSER_USERNAME --noinput

uwsgi --ini /code/docker/uwsgi/uwsgi.ini
