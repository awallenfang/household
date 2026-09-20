export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-root.prod_settings}"
celery -A root worker --autoscale=10,3 --loglevel=info