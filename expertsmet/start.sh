#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=expertsmet.settings_docker

APP_DIR="/app/expertsmet"
echo "Using application directory: ${APP_DIR}"
cd "${APP_DIR}"

echo "USE_SQLITE environment variable: ${USE_SQLITE}"

if [[ "${USE_SQLITE,,}" == "true" ]]; then
    echo "Using SQLite database - skipping PostgreSQL availability check"
else
    echo "Waiting for PostgreSQL database..."
    DB_HOST_ENV=${DB_HOST:-db}
    DB_PORT_ENV=${DB_PORT:-5432}
    while ! nc -z "${DB_HOST_ENV}" "${DB_PORT_ENV}"; do
        sleep 0.5
    done
    echo "PostgreSQL database is ready!"
fi

# Ensure runtime directories exist when volumes are mounted
mkdir -p logs staticfiles media

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py shell <<'PYTHON_EOF'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username=os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin'),
        email=os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@expertsmet.ru'),
        password=os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    )
    print('Superuser created successfully.')
else:
    print('Superuser already exists.')
PYTHON_EOF

exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 60 expertsmet.wsgi:application
