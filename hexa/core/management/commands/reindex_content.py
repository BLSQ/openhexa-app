from django.core.management.base import BaseCommand
from django.db import transaction

from hexa.plugins.app import get_connector_app_configs


class Command(BaseCommand):
    help = "Re-index all content"

    def handle(self, *args, **options):
        self.stdout.write(f"Re-indexing...")

        for app_config in get_connector_app_configs():
            app_models = list(app_config.get_models())
            indexed_models = [
                m
                for m in app_models
                if hasattr(m, "index") and callable(getattr(m, "index"))
            ]

            with transaction.atomic():
                self.stdout.write(f"Re-indexing content")
                for indexed_model in indexed_models:
                    for datasource in indexed_model.objects.all():
                        self.stdout.write(f"Re-indexing {datasource}")
                        datasource.save()

        self.stdout.write(self.style.SUCCESS("Done"))
