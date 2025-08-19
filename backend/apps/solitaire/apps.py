"""
Solitaire App Configuration
"""

from django.apps import AppConfig


class SolitaireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.solitaire'
    verbose_name = 'Solitaire Game'