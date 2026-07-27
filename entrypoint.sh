#!/bin/bash
set -e

echo "Starting Ecomman Django app..."

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
else
    echo "Skipping database migrations."
fi

if [ "${COLLECT_STATIC:-1}" = "1" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
else
    echo "Skipping static file collection."
fi

echo "Starting application..."
exec "$@"
