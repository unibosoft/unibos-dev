"""
Simple development settings for quick startup
"""
from .base import *

# Remove problematic apps temporarily
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in [
    'channels',
    'django_prometheus', 
    'debug_toolbar',
    'django_seed',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.celery',
    'health_check.contrib.redis',
]]

# Remove prometheus middleware
MIDDLEWARE = [m for m in MIDDLEWARE if 'prometheus' not in m]

# Simple SQLite database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable celery for now
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Allow all hosts for development
ALLOWED_HOSTS = ['*']

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'data_db' / 'media'

# Simplified logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Disable ASGI
WSGI_APPLICATION = 'unibos_backend.wsgi.application'