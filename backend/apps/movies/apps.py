from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.movies'
    verbose_name = 'movies'
    
    def ready(self):
        """Initialize app signals and handlers"""
        try:
            from . import signals
        except ImportError:
            pass