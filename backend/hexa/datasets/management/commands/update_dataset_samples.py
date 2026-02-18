# Update dataset files to change the sample and save the number of rows
from django.core.management.base import BaseCommand

from hexa.datasets.models import DatasetVersionFile


class Command(BaseCommand):
    help = "Update sample and rows fields"

    def handle(self, *args, **options):
        for dvf in DatasetVersionFile.objects.all():
            dvf.generate_metadata()
