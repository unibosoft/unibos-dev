"""
Core Tasks
Basic background tasks for UNIBOS
"""

from celery import shared_task


@shared_task(name='core.health_check')
def health_check():
    """
    Periodic health check task
    Returns system health status
    """
    import psutil
    import platform

    return {
        'status': 'healthy',
        'platform': platform.system(),
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
    }


@shared_task(name='core.cleanup_temp_files')
def cleanup_temp_files(max_age_hours: int = 24):
    """
    Clean up temporary files older than max_age_hours
    """
    import os
    import time
    from pathlib import Path

    temp_dir = Path('/tmp/unibos')
    if not temp_dir.exists():
        return {'cleaned': 0, 'status': 'no temp directory'}

    now = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned = 0

    for file_path in temp_dir.rglob('*'):
        if file_path.is_file():
            file_age = now - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    cleaned += 1
                except OSError:
                    pass

    return {'cleaned': cleaned, 'status': 'success'}


@shared_task(name='core.send_notification')
def send_notification(user_id: str, title: str, message: str, notification_type: str = 'info'):
    """
    Send notification to user
    """
    # Placeholder - integrate with notification system
    return {
        'user_id': user_id,
        'title': title,
        'message': message,
        'type': notification_type,
        'status': 'sent'
    }
