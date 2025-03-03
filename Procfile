web: gunicorn project.wsgi:application --workers 3 --timeout 120 --worker-class gthread --threads 2 --max-requests 1000 --max-requests-jitter 50
