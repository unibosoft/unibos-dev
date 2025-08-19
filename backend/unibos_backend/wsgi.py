"""
WSGI config for UNIBOS Backend project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')

application = get_wsgi_application()