from logging import getLogger

import tqdm as tqdm
from django.core.management.base import BaseCommand
from django.db import transaction

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
            print(f"- {app.verbose_name}")
            for model in models:
                if not issubclass(model, Datasource):
                    # ignore sync-able non datasource
                    continue

                with transaction.atomic():
                    instances = model.objects.all()
                    pbar = tqdm.tqdm(instances)
                    pbar.set_description(f"   {model.__name__:15}")
                    for instance in pbar:
                        try:
                            if instance.auto_sync:
                                instance.sync()
                        except Exception:
                            logger.exception("sync")
