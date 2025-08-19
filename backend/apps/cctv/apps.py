"""
CCTV Application Configuration
"""

from django.apps import AppConfig


class CCTVConfig(AppConfig):
    """CCTV application configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cctv'
    verbose_name = 'cctv security system'
    
    def ready(self):
        """Initialize app when Django starts"""
        # Import signal handlers when app is ready
        try:
            import apps.cctv.signals  # noqa
        except ImportError:
            pass