# Update dataset files to change the sample and save the number of rows
from django.core.management.base import BaseCommand
from django.db import transaction

from hexa.datasets.models import DatasetFileSample, DatasetVersionFile

BATCH_SIZE = 1000


class Command(BaseCommand):
    help = "Update sample and rows fields"

    def handle(self, *args, **options):
        for dvf in DatasetVersionFile.objects.all():
            dvf.generate_metadata()

    @staticmethod
    def _flush_batch(files, samples):
        """
        Flush a batch inside a short atomic transaction.
        Locks only the rows in this batch and only for a short time.
        """
        with transaction.atomic():
            DatasetVersionFile.objects.bulk_update(
                files,
                ["rows"],
                batch_size=len(files),
            )

            DatasetFileSample.objects.bulk_update(
                samples,
                ["sample"],
                batch_size=len(samples),
            )
