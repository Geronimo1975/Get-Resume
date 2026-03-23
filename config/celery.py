import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("lebenslauf_builder")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Define task queues
app.conf.task_routes = {
    "payments.tasks.*": {"queue": "payments"},
    "legal.tasks.*": {"queue": "gdpr"},
    "automation.tasks.send_*": {"queue": "emails"},
    "accounts.tasks.*": {"queue": "default"},
}

# Retry policy for transient failures
app.conf.task_default_retry_delay = 60
app.conf.task_max_retries = 3
