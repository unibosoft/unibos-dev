"""
UNIBOS Celery Application
Celery configuration for background task processing
"""

import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')

# Create Celery app
app = Celery('unibos')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in registered Django apps
app.autodiscover_tasks()

# Task routing configuration
app.conf.task_routes = {
    'core.profiles.worker.tasks.core.*': {'queue': 'default'},
    'core.profiles.worker.tasks.ocr.*': {'queue': 'ocr'},
    'core.profiles.worker.tasks.media.*': {'queue': 'media'},
}

# Default queue
app.conf.task_default_queue = 'default'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing"""
    print(f'Request: {self.request!r}')
