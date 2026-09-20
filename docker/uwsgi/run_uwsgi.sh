#! /bin/bash
set -e
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-root.prod_settings}"
export DEBUG="${DEBUG:-False}"

python - <<'EOF'
import os, socket, sys, time
host, port = os.environ.get("POSTGRES_HOST", "db"), int(os.environ.get("POSTGRES_PORT", "5432"))
for _ in range(60):
    try:
        socket.create_connection((host, port), timeout=2).close()
        break
    except OSError:
        time.sleep(1)
else:
    sys.exit("Timed out waiting for Postgres")
EOF

python manage.py migrate --noinput
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --username "$DJANGO_SUPERUSER_USERNAME" --noinput || true
fi
python manage.py compilemessages -v0 || true

python manage.py sass /code/hub/static/hub/scss /code/hub/static/hub/css -t compressed || true
python manage.py sass /code/todos/static/todos/scss /code/todos/static/todos/css -t compressed || true
python manage.py sass /code/space/static/space/scss /code/space/static/space/css -t compressed || true

python manage.py collectstatic --no-input

exec uwsgi --ini /code/docker/uwsgi/uwsgi.ini
