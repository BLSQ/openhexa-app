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
        indexables = ConnectorAppConfig.get_models_by_capability("index", filter_app)

        for app, models in indexables.items():
            for model in models:
                if not issubclass(model, Environment):
                    # ignore index-able non environment
                    continue

                for instance in model.objects.all():
                    try:
                        logger.info("building index %s:%s", model, instance.id)
                        with transaction.atomic():
                            instance.build_index()
                    except Exception:
                        logger.exception("index error")
