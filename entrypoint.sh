#!/bin/bash
# entrypoint.sh - run migrations, collectstatic, then start gunicorn

set -e

# wait for DB (simple loop)
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database to be ready..."
  # simple attempt to wait for DB -tries to run migrate which will fail until DB ready
fi

# run migrations and collectstatic
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# create superuser if env provided (non-interactive)
if [ ! -z "$DJANGO_SUPERUSER_USERNAME" ] && [ ! -z "$DJANGO_SUPERUSER_EMAIL" ] && [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser (if not exists)..."
  python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); \
    username='${DJANGO_SUPERUSER_USERNAME}'; \
    email='${DJANGO_SUPERUSER_EMAIL}'; \
    pwd='${DJANGO_SUPERUSER_PASSWORD}'; \
    User.objects.filter(username=username).exists() or User.objects.create_superuser(username, email, pwd)"
fi

# start Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
