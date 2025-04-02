from time import sleep

from django.core.management.base import BaseCommand

from hexa.plugins.connector_airflow.models import Cluster


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            dest="limit",
            help="Number of dag runs to track from the cluster",
            default=100,
            type=int,
        )

    def handle(self, *args, limit, **options):
        while True:
            for cluster in Cluster.objects.all():
                cluster.dag_runs_sync(limit)
                if options.get("_test_once") is True:
                    return
            sleep(60)
