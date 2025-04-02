from django.apps import AppConfig


class SoftDeleteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hexa.core.tests.soft_delete"
    label = "soft_delete"
