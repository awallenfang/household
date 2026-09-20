#!/bin/bash

echo "Running debug build"

echo "Waiting for Postgres"
python - <<'EOF'
import os, socket, time
host, port = os.environ.get("POSTGRES_HOST", "db"), int(os.environ.get("POSTGRES_PORT", "5432"))
for _ in range(60):
    try:
        socket.create_connection((host, port), timeout=2).close()
        break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("Timed out waiting for Postgres")
EOF

echo "Applying migrations"
python ./manage.py migrate --noinput

echo "Creating superuser"
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --username "$DJANGO_SUPERUSER_USERNAME" --noinput || true
fi

python manage.py sass /code/hub/static/hub/scss /code/hub/static/hub/css -t compressed --watch &
python manage.py sass /code/todos/static/todos/scss /code/todos/static/todos/css -t compressed --watch &
python manage.py sass /code/space/static/space/scss /code/space/static/space/css -t compressed --watch &

echo "Running celery"
celery -A root worker --loglevel=info -c 4 &
echo "Running celery beat"
celery -A root beat --loglevel=info  &

echo "Starting Django application"
python manage.py runserver 0.0.0.0:5000