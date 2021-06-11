from django.core.management.base import BaseCommand
from django.db import transaction

from hexa.catalog.models import CatalogIndex
from hexa.pipelines.models import PipelinesIndex
from hexa.plugins.app import get_connector_app_configs


class Command(BaseCommand):
    help = "Re-index all content"

    def handle(self, *args, **options):
        self.stdout.write(f"Re-indexing...")

        self.stdout.write("Deleting existing catalog indexes")
        CatalogIndex.objects.all().delete()
        self.stdout.write("Deleting existing pipelines indexes")
        PipelinesIndex.objects.all().delete()

        for app_config in get_connector_app_configs():
            app_model_classes = list(app_config.get_models())
            indexed_model_classes = [
                mc
                for mc in app_model_classes
                if hasattr(mc, "index") and callable(getattr(mc, "index"))
            ]

            with transaction.atomic():
                self.stdout.write(f"Re-indexing content for {app_config.label}")
                for indexed_model_class in indexed_model_classes:
                    for index_object in indexed_model_class.objects.all():
                        self.stdout.write(f"Re-indexing {index_object}")
                        index_object.save()

        self.stdout.write(self.style.SUCCESS("Done"))
