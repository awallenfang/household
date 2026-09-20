#! /bin/bash
set -e
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-root.prod_settings}"
export DEBUG="${DEBUG:-False}"

echo "Waiting for Postgres"
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

echo "Applying migrations"
python ./manage.py migrate --noinput

echo "Creating superuser"
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --username "$DJANGO_SUPERUSER_USERNAME" --noinput || true
else
  echo "DJANGO_SUPERUSER_USERNAME not set, skipping"
fi

echo "Running uwsgi server"
exec uwsgi --ini ./docker/uwsgi/uwsgi.ini