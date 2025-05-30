#! /bin/bash
python manage.py migrate
python manage.py createsuperuser --username $DJANGO_SUPERUSER_USERNAME --noinput
python manage.py compilemessages -v0

uwsgi --ini /code/docker/uwsgi/uwsgi.ini
