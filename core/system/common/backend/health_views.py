"""
Health Check Endpoints for UNIBOS Backend
Comprehensive health monitoring with detailed status reporting
"""

import time
import logging
from django.http import JsonResponse
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)


def get_version_info():
    """Get UNIBOS version information"""
    try:
        import json
        from pathlib import Path
        version_file = Path(settings.UNIBOS_ROOT) / 'VERSION.json'
        if version_file.exists():
            with open(version_file) as f:
                return json.load(f)
    except Exception:
        pass
    return {'version': getattr(settings, 'UNIBOS_VERSION', 'unknown')}


@api_view(['GET'])
@permission_classes([AllowAny])
def health_quick(request):
    """
    Quick health check - minimal overhead
    Used by load balancers and monitoring systems
    """
    return JsonResponse({
        'status': 'ok',
        'timestamp': time.time(),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_db(request):
    """
    Database connectivity health check
    Tests PostgreSQL connection and basic query
    """
    start_time = time.time()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()

        duration = (time.time() - start_time) * 1000  # ms
        return JsonResponse({
            'status': 'ok',
            'service': 'postgresql',
            'response_time_ms': round(duration, 2),
            'database': settings.DATABASES['default'].get('NAME', 'unknown'),
        })
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'service': 'postgresql',
            'error': str(e),
        }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_redis(request):
    """
    Redis connectivity health check
    Tests cache connection with set/get operation
    """
    start_time = time.time()
    try:
        test_key = 'health_check_test'
        test_value = f'test_{time.time()}'

        # Test write
        cache.set(test_key, test_value, timeout=10)

        # Test read
        result = cache.get(test_key)

        if result != test_value:
            raise Exception("Redis read/write mismatch")

        # Cleanup
        cache.delete(test_key)

        duration = (time.time() - start_time) * 1000  # ms
        return JsonResponse({
            'status': 'ok',
            'service': 'redis',
            'response_time_ms': round(duration, 2),
            'url': settings.REDIS_URL.split('@')[-1] if '@' in settings.REDIS_URL else settings.REDIS_URL,
        })
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'service': 'redis',
            'error': str(e),
        }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_celery(request):
    """
    Celery worker health check
    Tests if workers are responsive
    """
    start_time = time.time()
    try:
        from celery import current_app

        # Inspect workers
        inspector = current_app.control.inspect()

        # Check if any workers respond (with timeout)
        ping_results = inspector.ping()

        if not ping_results:
            return JsonResponse({
                'status': 'warning',
                'service': 'celery',
                'message': 'No workers responding',
                'workers': [],
            }, status=200)

        # Get worker stats
        workers = []
        active_tasks = inspector.active() or {}
        scheduled_tasks = inspector.scheduled() or {}

        for worker_name in ping_results.keys():
            workers.append({
                'name': worker_name,
                'status': 'ok',
                'active_tasks': len(active_tasks.get(worker_name, [])),
                'scheduled_tasks': len(scheduled_tasks.get(worker_name, [])),
            })

        duration = (time.time() - start_time) * 1000  # ms
        return JsonResponse({
            'status': 'ok',
            'service': 'celery',
            'response_time_ms': round(duration, 2),
            'workers': workers,
            'total_workers': len(workers),
        })
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'service': 'celery',
            'error': str(e),
        }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_channels(request):
    """
    Django Channels / WebSocket health check
    Tests Channel Layer connectivity
    """
    start_time = time.time()
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        # Test channel layer by sending/receiving a message
        test_channel = f"health_check_{int(time.time())}"
        test_message = {"type": "health.check", "data": "test"}

        # Simple connectivity test
        async_to_sync(channel_layer.group_add)(test_channel, "health_test")
        async_to_sync(channel_layer.group_discard)(test_channel, "health_test")

        duration = (time.time() - start_time) * 1000  # ms
        return JsonResponse({
            'status': 'ok',
            'service': 'channels',
            'response_time_ms': round(duration, 2),
            'backend': type(channel_layer).__name__,
        })
    except Exception as e:
        logger.error(f"Channels health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'service': 'channels',
            'error': str(e),
        }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_node(request):
    """
    Node identity health check
    Returns node information for multi-node architecture
    """
    try:
        from core.base.identity.identity import get_instance_identity

        identity = get_instance_identity()

        return JsonResponse({
            'status': 'ok',
            'service': 'node_identity',
            'node_uuid': identity.get_uuid(),
            'node_type': identity.get_node_type().value,
            'hostname': identity.identity.hostname,
            'platform': identity.identity.platform,
            'capabilities': {
                'django': identity.get_capabilities().can_run_django,
                'celery': identity.get_capabilities().can_run_celery,
                'websocket': identity.get_capabilities().can_run_websocket,
            }
        })
    except Exception as e:
        logger.error(f"Node identity health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'service': 'node_identity',
            'error': str(e),
        }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_full(request):
    """
    Comprehensive health check
    Aggregates all service checks into single response
    """
    overall_start = time.time()

    services = {}
    all_healthy = True

    # Database check
    try:
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        services['database'] = {
            'status': 'ok',
            'response_time_ms': round((time.time() - start) * 1000, 2),
        }
    except Exception as e:
        services['database'] = {'status': 'error', 'error': str(e)}
        all_healthy = False

    # Redis check
    try:
        start = time.time()
        test_key = 'health_full_test'
        cache.set(test_key, 'test', timeout=5)
        cache.get(test_key)
        cache.delete(test_key)
        services['redis'] = {
            'status': 'ok',
            'response_time_ms': round((time.time() - start) * 1000, 2),
        }
    except Exception as e:
        services['redis'] = {'status': 'error', 'error': str(e)}
        all_healthy = False

    # Celery check (non-blocking, may timeout)
    try:
        from celery import current_app
        inspector = current_app.control.inspect(timeout=2)
        ping_results = inspector.ping()

        if ping_results:
            services['celery'] = {
                'status': 'ok',
                'workers': len(ping_results),
            }
        else:
            services['celery'] = {
                'status': 'warning',
                'message': 'No workers responding',
            }
    except Exception as e:
        services['celery'] = {'status': 'error', 'error': str(e)}
        # Celery down is warning, not critical

    # Channels check
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        start = time.time()
        channel_layer = get_channel_layer()
        test_channel = f"health_{int(time.time())}"
        async_to_sync(channel_layer.group_add)(test_channel, "test")
        async_to_sync(channel_layer.group_discard)(test_channel, "test")

        services['channels'] = {
            'status': 'ok',
            'response_time_ms': round((time.time() - start) * 1000, 2),
        }
    except Exception as e:
        services['channels'] = {'status': 'error', 'error': str(e)}
        all_healthy = False

    # Node identity check
    try:
        from core.base.identity.identity import get_instance_identity
        identity = get_instance_identity()
        services['node'] = {
            'status': 'ok',
            'uuid': identity.get_uuid(),
            'type': identity.get_node_type().value,
        }
    except Exception as e:
        services['node'] = {'status': 'unavailable', 'error': str(e)}

    # Version info
    version_info = get_version_info()

    total_time = (time.time() - overall_start) * 1000  # ms

    response_data = {
        'status': 'ok' if all_healthy else 'degraded',
        'timestamp': time.time(),
        'response_time_ms': round(total_time, 2),
        'version': version_info.get('version', 'unknown'),
        'environment': getattr(settings, 'UNIBOS_ENVIRONMENT', 'unknown'),
        'debug': settings.DEBUG,
        'services': services,
    }

    status_code = 200 if all_healthy else 503
    return JsonResponse(response_data, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_ready(request):
    """
    Kubernetes readiness probe
    Returns 200 only if service is ready to accept traffic
    """
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()

        # Check Redis
        cache.set('ready_check', 'ok', timeout=5)
        if cache.get('ready_check') != 'ok':
            raise Exception("Redis not responding")

        return JsonResponse({'status': 'ready'})
    except Exception as e:
        logger.warning(f"Readiness check failed: {e}")
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
        }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_live(request):
    """
    Kubernetes liveness probe
    Returns 200 if service is alive (process is running)
    """
    return JsonResponse({'status': 'alive', 'timestamp': time.time()})
