"""
Production settings for UNIBOS Backend
"""

from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# Security
DEBUG = False

# HTTPS/SSL Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional security headers
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)

# Static files with compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_COMPRESS_OFFLINE = True
WHITENOISE_GZIP_EXCLUDE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000',
    'sslmode': 'require',
    'target_session_attrs': 'read-write',
    'keepalives': 1,
    'keepalives_idle': 30,
    'keepalives_interval': 10,
    'keepalives_count': 5,
}

# Cache configuration for production
CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS']['max_connections'] = 100
CACHES['default']['TIMEOUT'] = 600  # 10 minutes

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = 'unibos_sessionid'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 86400  # 24 hours

# CSRF security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = 'unibos_csrftoken'
CSRF_FAILURE_VIEW = 'apps.common.views.csrf_failure'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@unibos.com')

# Sentry Configuration
SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
        release=f"unibos@{UNIBOS_VERSION}",
    )

# Production logging
LOGGING['handlers']['file']['filename'] = '/var/log/unibos/django.log'
LOGGING['handlers']['security']['filename'] = '/var/log/unibos/security.log'

# Add error email handler
LOGGING['handlers']['mail_admins'] = {
    'level': 'ERROR',
    'filters': ['require_debug_false'],
    'class': 'django.utils.log.AdminEmailHandler',
}

LOGGING['loggers']['django.request'] = {
    'handlers': ['mail_admins', 'file'],
    'level': 'ERROR',
    'propagate': True,
}

# Performance optimizations
CONN_MAX_AGE = 600

# Template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# API Rate limiting for production
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',
    'user': '1000/hour',
    'burst': '60/minute',
    'sustained': '10000/day',
}

# Celery production settings
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False
CELERY_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True

# Admin notifications
ADMINS = [('Admin', env('ADMIN_EMAIL', default='admin@unibos.com'))]
MANAGERS = ADMINS
SERVER_EMAIL = 'server@unibos.com'

# File upload restrictions
FILE_UPLOAD_MAX_MEMORY_SIZE = 2.5 * 1024 * 1024  # 2.5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 2.5 * 1024 * 1024  # 2.5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Prevent host header attacks
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Health check settings
HEALTH_CHECK_APPS = [
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.celery',
    'health_check.contrib.redis',
]

INSTALLED_APPS += HEALTH_CHECK_APPS