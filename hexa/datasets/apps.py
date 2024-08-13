from django.apps import AppConfig
from django.conf import settings


class DatasetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hexa.datasets"

    def ready(self):
        from hexa.files import storage

        # Check if datasets bucket exists and create it if not

        if not storage.bucket_exists(settings.WORKSPACE_DATASETS_BUCKET):
            storage.create_bucket(settings.WORKSPACE_DATASETS_BUCKET)
