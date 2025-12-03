"""
Health Check URL Configuration
Provides comprehensive health monitoring endpoints
"""

from django.urls import path
from . import health_views

app_name = 'health'

urlpatterns = [
    # Quick health check (for load balancers)
    path('quick/', health_views.health_quick, name='quick'),

    # Individual service checks
    path('db/', health_views.health_db, name='db'),
    path('redis/', health_views.health_redis, name='redis'),
    path('celery/', health_views.health_celery, name='celery'),
    path('channels/', health_views.health_channels, name='channels'),
    path('node/', health_views.health_node, name='node'),

    # Comprehensive check
    path('full/', health_views.health_full, name='full'),

    # Kubernetes probes
    path('ready/', health_views.health_ready, name='ready'),
    path('live/', health_views.health_live, name='live'),

    # Root health endpoint (same as full)
    path('', health_views.health_full, name='root'),
]
