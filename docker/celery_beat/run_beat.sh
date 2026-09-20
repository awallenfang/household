export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-root.prod_settings}"
celery -A root beat -l INFO 
