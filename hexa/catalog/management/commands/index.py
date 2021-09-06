from typing import List, Dict

import tqdm as tqdm
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps, AppConfig
from django.db import transaction
from django.db.models.base import ModelBase

from hexa.plugins.app import ConnectorAppConfig


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--app", dest="filter_app", help="Limit the sync to a single app"
        )

    def handle(self, *args, filter_app, **options):
        indexables = ConnectorAppConfig.get_models_by_capability(
            "build_index", filter_app
        )

        for app, models in indexables.items():
            print(f"- {app.verbose_name}")
            for model in models:
                with transaction.atomic():
                    instances = model.objects.all()
                    pbar = tqdm.tqdm(instances)
                    pbar.set_description(f"   {model.__name__:15}")
                    for instance in pbar:
                        instance.build_index()
