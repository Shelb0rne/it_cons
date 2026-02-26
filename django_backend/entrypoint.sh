#!/bin/sh
set -eu

python - <<'PY'
import os
import sys
import time

import psycopg

host = os.getenv("DB_HOST", "postgres")
port = int(os.getenv("DB_PORT", "5432"))
dbname = os.getenv("DB_NAME", "it_cons")
user = os.getenv("DB_USER", "it_cons")
password = os.getenv("DB_PASSWORD", "it_cons")

for attempt in range(1, 61):
    try:
        conn = psycopg.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=3,
        )
        conn.close()
        print("Postgres is ready")
        break
    except Exception as exc:
        print(f"Waiting for Postgres ({attempt}/60): {exc}")
        time.sleep(1)
else:
    print("Postgres did not become ready in time", file=sys.stderr)
    sys.exit(1)
PY

python manage.py migrate --noinput
exec python manage.py runserver 0.0.0.0:${DJANGO_PORT:-8000}
