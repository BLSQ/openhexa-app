# Update dataset files to change the sample and save the number of rows
import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from hexa.datasets.models import DatasetFileSample, DatasetVersionFile
from hexa.datasets.queue import load_df

BATCH_SIZE = 1000


class Command(BaseCommand):
    help = "Update sample and rows fields"

    def handle(self, *args, **options):
        queryset = DatasetVersionFile.objects.filter(
            rows__isnull=True
        ).prefetch_related("samples")

        batch_files = []
        batch_samples = []

        total_files = 0
        total_samples = 0

        for version_file in queryset.iterator(chunk_size=1000):
            df = load_df(version_file)
            version_file.rows = len(df.index)
            batch_files.append(version_file)

            if not df.empty:
                sample = df.head(settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE)
                sample = sample.replace(
                    {np.inf: "inf", -np.inf: "-inf"}
                )  # We are not supporting Infinity as numbers
                sample = sample.to_dict(orient="records")
                for version_sample in version_file.samples.all():
                    version_sample.sample = sample
                    batch_samples.append(version_sample)

            if len(batch_files) >= BATCH_SIZE:
                self._flush_batch(batch_files, batch_samples)
                total_files += len(batch_files)
                total_samples += len(batch_samples)
                batch_files.clear()
                batch_samples.clear()

        # Flush remaining
        if batch_files:
            self._flush_batch(batch_files, batch_samples)
            total_files += len(batch_files)
            total_samples += len(batch_samples)

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {total_files} files and {total_samples} samples"
            )
        )

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
