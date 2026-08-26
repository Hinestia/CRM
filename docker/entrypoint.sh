#!/bin/sh
set -e

. "$(dirname "$0")/wait_for_db.sh"

# Миграции и сбор статики выполняются только контейнером web,
# чтобы celery worker/beat не гонялись за одной и той же миграцией.
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
