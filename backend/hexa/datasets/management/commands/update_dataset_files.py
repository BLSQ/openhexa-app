# Update dataset files to change the sample and save the number of rows
# References:
# https://github.com/BLSQ/openhexa-app/pull/1613
# https://github.com/BLSQ/openhexa-app/pull/1615
import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from hexa.datasets.models import DatasetVersionFile, DatasetFileSample
from hexa.datasets.queue import load_df


class Command(BaseCommand):
    help = "Update sample and rows fields"

    def handle(self, *args, **options):
        queryset = (
            DatasetVersionFile.objects
            .prefetch_related("samples")
        )

        files_to_update = []
        samples_to_update = []

        for version_file in queryset.iterator(chunk_size=1000):
            df = load_df(version_file)
            version_file.rows = len(df.index)
            files_to_update.append(version_file)

            for version_sample in version_file.samples.all():
                if not df.empty:
                    sample = df.head(settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE)
                    sample = sample.replace(
                        {np.inf: "inf", -np.inf: "-inf"}
                    )  # We are not supporting Infinity as numbers
                    version_sample.sample = sample.to_dict(orient="records")
                samples_to_update.append(version_sample)

        with transaction.atomic():
            if files_to_update:
                DatasetVersionFile.objects.bulk_update(
                    files_to_update,
                    ["rows"],
                    batch_size=1000,
                )

            if samples_to_update:
                DatasetFileSample.objects.bulk_update(
                    samples_to_update,
                    ["sample"],
                    batch_size=1000,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {len(files_to_update)} files and {len(samples_to_update)} samples"
            )
        )
