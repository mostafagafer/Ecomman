import os

from celery import Celery
# import logging

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# @app.task(bind=True, ignore_result=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')

# # Configure Celery's logging
# app.conf.update(
#     worker_log_format="%(asctime)s - %(levelname)s - %(message)s",
#     worker_task_log_format="%(asctime)s - %(levelname)s - Task %(task_name)s - %(message)s",
# )

# # Optional: Set the log level for your Celery worker
# app.conf.update(
#     worker_log_level="INFO",
# )

# # Set the path for the log file
# logging.basicConfig(
#     filename='celery_worker.log',  # You can change the filename and path here
#     level=logging.DEBUG,  # Adjust log level as needed
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )
