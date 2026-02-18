from datetime import timedelta

from django.test import TransactionTestCase
from django.utils import timezone

from hexa.core.test.migrator import Migrator
from hexa.datasets.models import DatasetVersion, DatasetVersionFile, DatasetFileSample


class Migration00XXDatasetFileSampleOneToOneTest(TransactionTestCase):
    migrate_from = ("datasets", "0017_datasetversionfile_rows")
    migrate_to = ("datasets", "0018_alter_datasetfilesample_dataset_version_file")  # adjust

    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(*self.migrate_from)

        # Create one version file
        self.version_file = self.get_version_file_model().objects.create(
            dataset_version=self.get_dataset_version()
        )

        # Create multiple samples pointing to same file (duplicates)
        self.sample_old = self.get_sample_model().objects.create(
            dataset_version_file=self.version_file,
            sample=[{"a": 1}],
            created_at=timezone.now(),
        )
        self.sample_new = self.get_sample_model().objects.create(
            dataset_version_file=self.version_file,
            sample=[{"a": 2}],
            created_at=timezone.now() + timedelta(seconds=1),
        )

        # Migrate forward
        self.migrator.migrate(*self.migrate_to)

        # Post-migration models
        self.DatasetVersionFile = self.get_version_file_model()
        self.DatasetFileSample = self.get_sample_model()

    def get_dataset_version(self) -> DatasetVersion:
        Dataset = self.migrator.apps.get_model("datasets", "Dataset")
        DatasetVersion = self.migrator.apps.get_model("datasets", "DatasetVersion")
        dataset = Dataset.objects.create()
        return DatasetVersion.objects.create(dataset=dataset)

    def get_version_file_model(self) -> DatasetVersionFile:
        return self.migrator.apps.get_model("datasets", "DatasetVersionFile")

    def get_sample_model(self) -> DatasetFileSample:
        return self.migrator.apps.get_model("datasets", "DatasetFileSample")

    def test_only_one_sample_per_file_after_migration(self):
        """Deduplication keeps exactly one sample per DatasetVersionFile."""
        samples = self.DatasetFileSample.objects.filter(
            dataset_version_file=self.version_file.pk
        )
        self.assertEqual(1, samples.count())

    def test_keeps_latest_sample(self):
        """The newest sample should be preserved after deduplication."""
        sample = self.DatasetFileSample.objects.get(
            dataset_version_file=self.version_file.pk
        )
        self.assertEqual([{"a": 2}], sample.sample)

    def test_dataset_version_file_not_deleted(self):
        """Migration must NOT delete DatasetVersionFile rows."""
        exists = self.DatasetVersionFile.objects.filter(
            pk=self.version_file.pk
        ).exists()
        self.assertTrue(exists)

    def test_cascade_direction_file_to_sample(self):
        """Deleting file should delete its sample (CASCADE)."""
        file_obj = self.DatasetVersionFile.objects.get(pk=self.version_file.pk)
        file_obj.delete()

        self.assertFalse(
            self.DatasetFileSample.objects.filter(
                dataset_version_file=self.version_file.pk
            ).exists()
        )

    def test_no_reverse_cascade_sample_to_file(self):
        """Deleting sample should NOT delete DatasetVersionFile."""
        sample = self.DatasetFileSample.objects.get(
            dataset_version_file=self.version_file.pk
        )
        sample.delete()

        self.assertTrue(
            self.DatasetVersionFile.objects.filter(
                pk=self.version_file.pk
            ).exists()
        )

    def test_one_to_one_enforced(self):
        """Creating a second sample for same file should fail."""
        file_obj = self.DatasetVersionFile.objects.get(pk=self.version_file.pk)

        with self.assertRaises(Exception):
            self.DatasetFileSample.objects.create(
                dataset_version_file=file_obj,
                sample=[{"x": 1}],
            )
