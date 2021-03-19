from django.core.management.base import BaseCommand
from django.db import transaction

from hexa.catalog.connectors import get_connector_app_configs
from hexa.catalog.models import Datasource, Content


class Command(BaseCommand):
    help = "Re-index the whole catalog"

    def handle(self, *args, **options):
        self.stdout.write(f"Re-indexing...")

        for app_config in get_connector_app_configs():
            app_models = list(app_config.get_models())
            datasource_models = [m for m in app_models if issubclass(m, Datasource)]
            content_models = [m for m in app_models if issubclass(m, Content)]

            with transaction.atomic():
                self.stdout.write(f"Re-indexing datasources")
                for datasource_model in datasource_models:
                    for datasource in datasource_model.objects.all():
                        self.stdout.write(f"Re-indexing {datasource}")
                        datasource.save()

                self.stdout.write(f"Re-indexing content")
                for content_model in content_models:
                    for content in content_model.objects.all():
                        self.stdout.write(f"Re-indexing {content }")
                        content.save()

        self.stdout.write(self.style.SUCCESS("Done"))
