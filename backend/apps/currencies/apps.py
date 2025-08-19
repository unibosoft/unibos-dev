"""
Currencies app configuration
"""

from django.apps import AppConfig


class CurrenciesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.currencies'
    verbose_name = 'Currencies Module'
    
    def ready(self):
        """
        Initialize app when Django starts
        """
        # Import signal handlers if any
        try:
            from . import signals
        except ImportError:
            pass