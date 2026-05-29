from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .management import create_permissions

class PermissionConfig(AppConfig):
    name = 'permission'

    def ready(self):
        post_migrate.connect(
            create_permissions,
            dispatch_uid = "django.contrib.auth.management.create_permissions",
        )
