from logging import getLogger

from django.core.management.base import BaseCommand

from hexa.catalog.models import Datasource
from hexa.plugins.app import ConnectorAppConfig

logger = getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--app", dest="filter_app", help="Limit the sync to a single app"
        )

    def handle(self, *args, filter_app, **options):
        syncables = ConnectorAppConfig.get_models_by_capability("sync", filter_app)

        for app, models in syncables.items():
            for model in models:
                if not issubclass(model, Datasource):
                    # ignore sync-able non datasource
                    continue

                for instance in model.objects.all():
                    if not instance.auto_sync:
                        logger.info(
                            "sync datasource %s:%s skipped",
                            model,
                            instance.display_name,
                        )
                        continue

                    try:
                        logger.info(
                            "sync datasource %s:%s", model, instance.display_name
                        )
                        instance.sync()
                    except Exception:
                        logger.exception("sync error")
