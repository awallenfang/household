#! /bin/bash
python manage.py migrate
python manage.py createsuperuser --username $DJANGO_SUPERUSER_USERNAME --noinput
python manage.py compilemessages -v0
python manage.py sass /code/hub/static/hub/scss /code/hub/static/hub/css -t compressed
python manage.py sass /code/todos/static/todos/scss /code/todos/static/todos/css -t compressed
python manage.py sass /code/space/static/space/scss /code/space/static/space/css -t compressed

uwsgi --ini /code/docker/uwsgi/uwsgi.ini
