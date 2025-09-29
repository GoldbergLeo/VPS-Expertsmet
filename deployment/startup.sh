#!/bin/bash

set -e

echo "Starting Expertsmet deployment..."

# Wait for database if needed (not used with SQLite but good practice)
echo "Running database migrations..."
python manage.py migrate --settings=expertsmet.settings_production

# Collect static files (just in case)
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=expertsmet.settings_production

# Create superuser if specified
if [ ! -z "$DJANGO_SUPERUSER_EMAIL" ] && [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py shell --settings=expertsmet.settings_production -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser('admin', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
fi

# Start nginx
echo "Starting nginx..."
nginx -t
service nginx start

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn expertsmet.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 60 \
    --keep-alive 2 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -