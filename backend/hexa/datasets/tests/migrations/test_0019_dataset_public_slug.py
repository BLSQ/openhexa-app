from datetime import timedelta
from unittest.mock import patch

from django.test import TransactionTestCase
from django.utils import timezone

from hexa.core.test.migrator import Migrator


class Migration0019DatasetPublicSlugTest(TransactionTestCase):
    migrate_from = ("datasets", "0018_alter_datasetfilesample_dataset_version_file")
    migrate_to = ("datasets", "0019_dataset_public_slug")

    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(*self.migrate_from)
        Dataset = self.migrator.apps.get_model("datasets", "Dataset")

        now = timezone.now()
        self.oldest = Dataset.objects.create(name="Shared", slug="shared")
        self.newest = Dataset.objects.create(name="Shared", slug="shared")
        self.reserved = Dataset.objects.create(name="New", slug="new")
        Dataset.objects.filter(pk=self.oldest.pk).update(created_at=now)
        Dataset.objects.filter(pk=self.newest.pk).update(
            created_at=now + timedelta(seconds=1)
        )

        with patch("secrets.token_hex", return_value="123"):
            self.migrator.migrate(*self.migrate_to)
        self.Dataset = self.migrator.apps.get_model("datasets", "Dataset")

    def test_oldest_dataset_keeps_slug(self):
        self.assertEqual(
            self.Dataset.objects.get(pk=self.oldest.pk).public_slug, "shared"
        )

    def test_later_duplicate_gets_suffix(self):
        self.assertEqual(
            self.Dataset.objects.get(pk=self.newest.pk).public_slug, "shared-123"
        )

    def test_reserved_slug_gets_suffix(self):
        self.assertEqual(
            self.Dataset.objects.get(pk=self.reserved.pk).public_slug, "new-123"
        )
