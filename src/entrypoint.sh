#!/bin/bash
set -e

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

gunicorn core.wsgi -b 0.0.0.0:8000


exec "$@"