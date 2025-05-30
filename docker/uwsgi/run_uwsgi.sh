#! /bin/bash
python manage.py migrate
python manage.py createsuperuser --username $DJANGO_SUPERUSER_USERNAME --noinput
cd hub & python ../manage.py compilemessages & cd ..
cd todos & python ../manage.py compilemessages & cd ..
cd space & python ../manage.py compilemessages & cd ..

uwsgi --ini /code/docker/uwsgi/uwsgi.ini
