from logging import getLogger

from django.core.management.base import BaseCommand
from django.db import transaction

from hexa.pipelines.models import Environment
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
                if not issubclass(model, Environment):
                    # ignore sync-able non environment
                    continue

                for instance in model.objects.all():
                    if not instance.auto_sync:
                        logger.info(
                            "sync environment %s:%s skipped", model, instance.id
                        )
                        continue
                    try:
                        logger.info("sync environment %s:%s", model, instance.id)
                        with transaction.atomic():
                            instance.sync()
                    except Exception:
                        logger.exception("sync error")
