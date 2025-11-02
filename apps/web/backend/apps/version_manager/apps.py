from django.apps import AppConfig


class VersionManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.version_manager'
    verbose_name = 'Version Manager'
