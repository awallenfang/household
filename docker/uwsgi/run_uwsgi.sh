#! /bin/bash
python manage.py migrate
uwsgi --ini /code/docker/uwsgi/uwsgi.ini
