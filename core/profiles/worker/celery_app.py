"""
UNIBOS Celery Application
Celery configuration for background task processing

Usage:
    # Start worker
    celery -A core.profiles.worker.celery_app worker -l INFO

    # Start beat scheduler
    celery -A core.profiles.worker.celery_app beat -l INFO

    # Start both (dev only)
    celery -A core.profiles.worker.celery_app worker -B -l INFO
"""

import os
import sys
from pathlib import Path
from celery import Celery
from celery.schedules import crontab

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'core' / 'clients' / 'web'))

# Set default Django settings module based on environment
# Can be overridden by DJANGO_SETTINGS_MODULE env var
default_settings = os.environ.get('UNIBOS_SETTINGS', 'hub')
settings_map = {
    'hub': 'unibos_backend.settings.hub',
    'node': 'unibos_backend.settings.node',
    'worker': 'unibos_backend.settings.worker',
    'dev': 'unibos_backend.settings.development',
}
django_settings = settings_map.get(default_settings, 'unibos_backend.settings.hub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings)

# Create Celery app
app = Celery('unibos')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Task routing configuration
app.conf.task_routes = {
    # Core tasks -> default queue
    'core.health_check': {'queue': 'default'},
    'core.cleanup_temp_files': {'queue': 'default'},
    'core.send_notification': {'queue': 'default'},
    'core.schedule_backup': {'queue': 'default'},
    'core.aggregate_metrics': {'queue': 'default'},
    # OCR tasks -> ocr queue
    'ocr.*': {'queue': 'ocr'},
    # Media tasks -> media queue
    'media.*': {'queue': 'media'},
}

# Default queue
app.conf.task_default_queue = 'default'

# Beat scheduler configuration (periodic tasks)
app.conf.beat_schedule = {
    # Health check every 5 minutes
    'health-check-every-5-min': {
        'task': 'core.health_check',
        'schedule': 300.0,  # 5 minutes
        'options': {'queue': 'default'},
    },
    # Cleanup temp files daily at 3 AM
    'cleanup-temp-daily': {
        'task': 'core.cleanup_temp_files',
        'schedule': crontab(hour=3, minute=0),
        'args': (24,),  # max_age_hours
        'options': {'queue': 'default'},
    },
    # Aggregate metrics hourly
    'aggregate-metrics-hourly': {
        'task': 'core.aggregate_metrics',
        'schedule': crontab(minute=0),  # Every hour at :00
        'args': ('hourly',),
        'options': {'queue': 'default'},
    },
}

# Timezone for beat scheduler
app.conf.timezone = 'Europe/Istanbul'

# Auto-discover tasks from worker tasks directory
app.autodiscover_tasks([
    'core.profiles.worker.tasks',
])


@app.task(bind=True, ignore_result=True, name='debug.task')
def debug_task(self):
    """Debug task for testing"""
    print(f'Request: {self.request!r}')
    return {'status': 'ok', 'worker': self.request.hostname}
