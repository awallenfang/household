#!/bin/bash
set -e

echo "Running test docker file"

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

echo "Running tests"
exec python manage.py test