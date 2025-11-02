"""
Birlikteyiz Django App Configuration
Emergency mesh network and earthquake monitoring
"""

from django.apps import AppConfig


class BirlikteyizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.birlikteyiz'
    verbose_name = 'birlikteyiz - emergency network'

    def ready(self):
        """
        Import signals when app is ready
        This ensures Django signals are registered
        """
        import apps.birlikteyiz.signals  # noqa
