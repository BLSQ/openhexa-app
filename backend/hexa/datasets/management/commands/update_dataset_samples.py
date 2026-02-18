# Update dataset files to change the sample and save the number of rows
from django.core.management.base import BaseCommand

from hexa.datasets.models import DatasetVersionFile


class Command(BaseCommand):
    help = "Regenerate metadata and preview for all dataset version files"

    def handle(self, *args, **options):
        for dvf in DatasetVersionFile.objects.all():
            dvf.generate_metadata()
