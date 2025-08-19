from django.apps import AppConfig


class MusicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.music'
    verbose_name = 'music'
    
    def ready(self):
        """Initialize app signals and handlers"""
        try:
            from . import signals
        except ImportError:
            pass