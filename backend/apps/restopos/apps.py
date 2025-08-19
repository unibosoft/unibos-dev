from django.apps import AppConfig


class RestoPOSConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.restopos'
    verbose_name = 'restaurant pos'
    
    def ready(self):
        """Initialize app signals and handlers"""
        try:
            from . import signals
        except ImportError:
            pass