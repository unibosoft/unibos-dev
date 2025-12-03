"""
Django App Configuration for Node Registry
"""

from django.apps import AppConfig


class NodesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.system.nodes.backend'
    label = 'nodes'
    verbose_name = 'Node Registry'

    def ready(self):
        # Import signals if needed
        pass
