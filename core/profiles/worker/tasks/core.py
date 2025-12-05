"""
Core Tasks
Basic background tasks for UNIBOS
"""

import os
import time
import platform
from datetime import datetime, timedelta
from pathlib import Path
from celery import shared_task


@shared_task(name='core.health_check')
def health_check():
    """
    Periodic health check task
    Returns system health status
    """
    try:
        import psutil

        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
        }
    except ImportError:
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'platform': platform.system(),
            'note': 'psutil not installed for detailed metrics',
        }


@shared_task(name='core.cleanup_temp_files')
def cleanup_temp_files(max_age_hours: int = 24, base_path: str = None):
    """
    Clean up temporary files older than max_age_hours

    Args:
        max_age_hours: Maximum age of files to keep (default: 24 hours)
        base_path: Base path to clean (default: /tmp/unibos)

    Returns:
        Dict with cleanup statistics
    """
    temp_dir = Path(base_path) if base_path else Path('/tmp/unibos')

    if not temp_dir.exists():
        return {
            'cleaned': 0,
            'status': 'no temp directory',
            'path': str(temp_dir),
        }

    now = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned = 0
    errors = 0
    total_size = 0

    for file_path in temp_dir.rglob('*'):
        if file_path.is_file():
            try:
                file_age = now - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    cleaned += 1
                    total_size += file_size
            except OSError:
                errors += 1

    return {
        'cleaned': cleaned,
        'errors': errors,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'status': 'success',
        'path': str(temp_dir),
    }


@shared_task(name='core.send_notification', bind=True, max_retries=3)
def send_notification(self, user_id: str, title: str, message: str,
                      notification_type: str = 'info', channels: list = None):
    """
    Send notification to user via multiple channels

    Args:
        user_id: Unique user identifier
        title: Notification title
        message: Notification message body
        notification_type: Type of notification (info, warning, error, success)
        channels: List of channels to send to (push, email, websocket)

    Returns:
        Dict with notification status
    """
    channels = channels or ['push']
    results = {}

    for channel in channels:
        try:
            if channel == 'push':
                # TODO: Integrate with push notification service (FCM, APNs)
                results['push'] = {'status': 'placeholder', 'message': 'Push not yet implemented'}

            elif channel == 'email':
                # TODO: Integrate with email service
                results['email'] = {'status': 'placeholder', 'message': 'Email not yet implemented'}

            elif channel == 'websocket':
                # TODO: Integrate with WebSocket notification
                results['websocket'] = {'status': 'placeholder', 'message': 'WebSocket not yet implemented'}

        except Exception as e:
            results[channel] = {'status': 'error', 'message': str(e)}

    return {
        'user_id': user_id,
        'title': title,
        'message': message,
        'type': notification_type,
        'channels': results,
        'timestamp': datetime.now().isoformat(),
    }


@shared_task(name='core.schedule_backup')
def schedule_backup(backup_type: str = 'full', target: str = 'local'):
    """
    Schedule a database backup task

    Args:
        backup_type: Type of backup (full, incremental)
        target: Backup target (local, remote, s3)

    Returns:
        Dict with backup scheduling info
    """
    # This task would typically trigger the actual backup
    return {
        'status': 'scheduled',
        'backup_type': backup_type,
        'target': target,
        'scheduled_at': datetime.now().isoformat(),
        'note': 'Backup will be executed by the backup worker',
    }


@shared_task(name='core.aggregate_metrics')
def aggregate_metrics(period: str = 'hourly'):
    """
    Aggregate system metrics for reporting

    Args:
        period: Aggregation period (hourly, daily, weekly)

    Returns:
        Dict with aggregated metrics
    """
    # TODO: Implement actual metrics aggregation from database
    return {
        'status': 'completed',
        'period': period,
        'aggregated_at': datetime.now().isoformat(),
        'metrics': {
            'api_requests': 0,
            'active_users': 0,
            'tasks_processed': 0,
            'errors': 0,
        },
        'note': 'Metrics aggregation placeholder',
    }
