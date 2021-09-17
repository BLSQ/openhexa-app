from typing import Dict, List

import tqdm as tqdm
from django.apps import AppConfig, apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.base import ModelBase

from hexa.plugins.app import ConnectorAppConfig


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--app", dest="filter_app", help="Limit the sync to a single app"
        )

    def handle(self, *args, filter_app, **options):
        indexables = ConnectorAppConfig.get_models_by_capability("index", filter_app)

        for app, models in indexables.items():
            print(f"- {app.verbose_name}")
            for model in models:
                with transaction.atomic():
                    instances = model.objects.all()
                    pbar = tqdm.tqdm(instances)
                    pbar.set_description(f"   {model.__name__:15}")
                    for instance in pbar:
                        instance.build_index()
