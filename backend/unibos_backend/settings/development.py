"""
Development settings - PostgreSQL
"""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# PostgreSQL for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unibos_db',
        'USER': 'unibos_user',
        'PASSWORD': 'unibos_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

print("💻 Development settings with PostgreSQL")
