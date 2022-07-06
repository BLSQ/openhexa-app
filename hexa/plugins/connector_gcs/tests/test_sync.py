import unittest.mock
from datetime import datetime, timezone

from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.test import TestCase
from hexa.plugins.connector_gcs.models import Bucket, Credentials


class SyncTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.credentials = Credentials.objects.create(
            service_account="",
            project_id="",
            client_id="",
            client_email="",
            client_x509_cert_url="",
            private_key_id="",
            private_key="",
        )
        cls.bucket = Bucket.objects.create(name="test-bucket")

    def test_empty_sync(self):
        self.assertEqual(self.bucket.object_set.count(), 0)
        with unittest.mock.patch(
            "hexa.plugins.connector_gcs.models.list_objects_metadata"
        ) as mocked_list_objects_metadata:
            mocked_list_objects_metadata.return_value = []
            self.bucket.sync()
        self.assertQuerysetEqual(self.bucket.object_set.all(), [])

    def test_sync_base(self):
        with unittest.mock.patch(
            "hexa.plugins.connector_gcs.models.list_objects_metadata"
        ) as mocked_list_objects_metadata:
            mocked_list_objects_metadata.return_value = [
                {
                    "name": "f1",
                    "size": 2,
                    "updated": datetime(2022, 6, 10, 13, 30, tzinfo=timezone.utc),
                    "etag": "CP769OOOnvgCEAI=",
                    "type": "file",
                },
                {
                    "name": "d1/",
                    "size": 0,
                    "updated": datetime(2022, 6, 10, 13, 30, tzinfo=timezone.utc),
                    "etag": "CM6Kxa/0nfgCEAE=",
                    "type": "directory",
                },
                {
                    "name": "d1/f2",
                    "size": 4,
                    "updated": datetime(2022, 6, 10, 13, 30, tzinfo=timezone.utc),
                    "etag": "CKqTpsKOnvgCEAI=",
                    "type": "file",
                },
            ]
            sync_result = self.bucket.sync()
            self.assertEqual(self.bucket.object_set.count(), 3)
            self.assertEqual(sync_result.created, 3)

            # Sync again, should not differ
            sync_result = self.bucket.sync()
            self.assertEqual(self.bucket.object_set.count(), 3)
            self.assertEqual(sync_result.identical, 3)

    def test_sync_remove_add(self):
        with unittest.mock.patch(
            "hexa.plugins.connector_gcs.models.list_objects_metadata"
        ) as mocked_list_objects_metadata:
            mocked_list_objects_metadata.return_value = [
                {
                    "name": "f1",
                    "size": 2,
                    "updated": datetime(2022, 6, 10, 13, 30, tzinfo=timezone.utc),
                    "etag": "CP769OOOnvgCEAI=",
                    "type": "file",
                },
                {
                    "name": "d1/",
                    "size": 0,
                    "updated": datetime(2022, 6, 10, 13, 30, tzinfo=timezone.utc),
                    "etag": "CM6Kxa/0nfgCEAE=",
                    "type": "directory",
                },
                {
                    "name": "d1/f2",
                    "size": 4,
                    "updated": datetime(2022, 6, 10, 13, 30, tzinfo=timezone.utc),
                    "etag": "CKqTpsKOnvgCEAI=",
                    "type": "file",
                },
            ]

            # Sync a first time
            sync_result = self.bucket.sync()
            self.assertEqual(
                DatasourceSyncResult(datasource=self.bucket, created=3), sync_result
            )

            # Delete f1, add f3 & f4
            mocked_list_objects_metadata.return_value = [
                {
                    "name": "d1/",
                    "size": 0,
                    "updated": datetime(2022, 6, 10, 13, 30, tzinfo=timezone.utc),
                    "etag": "CM6Kxa/0nfgCEAE=",
                    "type": "directory",
                },
                {
                    "name": "d1/f2",
                    "size": 4,
                    "updated": datetime(2022, 6, 10, 13, 30, tzinfo=timezone.utc),
                    "etag": "CKqTpsKOnvgCEAI=",
                    "type": "file",
                },
                {
                    "name": "d1/f3",
                    "size": 16,
                    "updated": datetime(2022, 6, 13, 13, 30, tzinfo=timezone.utc),
                    "etag": "CKqqgt7M9fcCEAE=",
                    "type": "file",
                },
                {
                    "name": "f4",
                    "size": 4,
                    "updated": datetime(2022, 6, 12, 13, 30, tzinfo=timezone.utc),
                    "etag": "CP119O25nvgCAAI=",
                    "type": "file",
                },
            ]

            # Sync again
            sync_result = self.bucket.sync()
            self.assertEqual(
                DatasourceSyncResult(
                    datasource=self.bucket, created=2, identical=2, deleted=1
                ),
                sync_result,
            )
