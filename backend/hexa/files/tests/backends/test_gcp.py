from unittest.mock import patch

from google.cloud.exceptions import NotFound

from hexa.core.test import TestCase
from hexa.files.backends.gcp import GoogleCloudStorage
from hexa.files.tests.mocks.client import MockClient


class GoogleCloudStorageTest(TestCase):
    storage = None

    def setUp(self):
        super().setUp()
        self.get_storage_client_patch = patch(
            "hexa.files.backends.gcp.get_storage_client"
        )
        self.mock_get_client = self.get_storage_client_patch.start()
        self.storage_client = MockClient()
        self.mock_get_client.return_value = self.storage_client
        self.storage = GoogleCloudStorage(
            service_account_key="service_account_key", region="europe-west1"
        )

        self.addCleanup(self.get_storage_client_patch.stop)

    def test_mock_client(self):
        self.assertIsInstance(self.storage.client, MockClient)
        with self.assertRaises(NotFound):
            self.storage.client.get_bucket("test-bucket")

    def test_create_bucket(self):
        self.storage.create_bucket("my-bucket")
        self.assertTrue(self.storage.bucket_exists("my-bucket"))

    def test_create_bucket_already_exists(self):
        self.storage.create_bucket("my-bucket")
        with self.assertRaises(self.storage.exceptions.AlreadyExists):
            self.storage.create_bucket("my-bucket")

    def test_list_bucket_objects(self):
        bucket_name = self.storage.create_bucket("my-bucket")
        bucket = self.storage_client.get_bucket(bucket_name)
        bucket.blob("test.txt").upload_from_string(b"test")
        items = self.storage.list_bucket_objects("my-bucket").items
        self.assertEqual(len(items), 1)
        first = items[0]
        self.assertEqual(first.name, "test.txt")

    def test_list_bucket_objects_with_match_glob(self):
        bucket_name = self.storage.create_bucket("my-bucket")
        bucket = self.storage_client.get_bucket(bucket_name)

        bucket.blob("testAAA.txt").upload_from_string(b"test")
        bucket.blob("testAAB.txt").upload_from_string(b"test")
        bucket.blob(".testAAB.txt").upload_from_string(b"Hidden file")
        bucket.blob("testABC.txt").upload_from_string(b"test")
        bucket.blob("testABD.txt").upload_from_string(b"test")

        items = self.storage.list_bucket_objects(
            "my-bucket", match_glob="*testAA*"
        ).items
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].name, "testAAA.txt")
        self.assertEqual(items[1].name, "testAAB.txt")

    def test_list_bucket_objects_prefixes_across_pages(self):
        """Subdirectories (prefixes) split across GCP API pages must all be returned.

        GCP's list_blobs paginates results, and prefixes are only revealed as their
        page is loaded. With a small page_size, some subdirectories end up on later
        pages. This test verifies that they are not silently dropped.
        """
        bucket_name = self.storage.create_bucket("my-bucket")
        bucket = self.storage_client.get_bucket(bucket_name)

        # Create 11 subdirectories.
        # With per_page=5, the GCP API page_size is 10 (per_page * 2),
        # so items are split across 2 API pages.
        # Page 3 should contain the 11th folder.
        for i in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]:
            bucket.blob(f"folder_{i}/").upload_from_string(b"")

        # Page 1:
        result = self.storage.list_bucket_objects("my-bucket", page=1, per_page=5)
        self.assertEqual(
            [item.name for item in result.items],
            [f"folder_{i}" for i in ["a", "b", "c", "d", "e"]],
        )

        # Page 2:
        result = self.storage.list_bucket_objects("my-bucket", page=2, per_page=5)
        self.assertEqual(
            [item.name for item in result.items],
            [f"folder_{i}" for i in ["f", "g", "h", "i", "j"]],
        )

        # Page 3:
        result = self.storage.list_bucket_objects("my-bucket", page=3, per_page=5)
        self.assertIn("folder_k", [item.name for item in result.items])

    def test_list_bucket_objects_late_prefix_not_dropped(self):
        """A folder that sorts after many files still appears prefix-first.

        When a single folder (zzz/) sorts alphabetically after many files,
        GCP places it on a late API page. It must still be discovered and
        yielded before files on every app page request.
        """
        bucket_name = self.storage.create_bucket("my-bucket")
        bucket = self.storage_client.get_bucket(bucket_name)

        # 12 files + 1 folder that sorts last alphabetically.
        # With per_page=5, GCP page_size=10, so 13 items span 2 GCP pages.
        # "zzz/" lands on GCP page 2, but must appear first in app results.
        for i in range(12):
            bucket.blob(f"file_{i:03d}.txt").upload_from_string(b"data")
        bucket.blob("zzz/").upload_from_string(b"")

        # App page 1: the folder comes first, followed by the first 4 files
        result = self.storage.list_bucket_objects("my-bucket", page=1, per_page=5)
        self.assertEqual(
            [item.name for item in result.items],
            ["zzz", "file_000.txt", "file_001.txt", "file_002.txt", "file_003.txt"],
        )

        # App page 2: next 5 files
        result = self.storage.list_bucket_objects("my-bucket", page=2, per_page=5)
        self.assertEqual(
            [item.name for item in result.items],
            ["file_004.txt", "file_005.txt", "file_006.txt", "file_007.txt", "file_008.txt"],
        )

        # App page 3: remaining 3 files
        result = self.storage.list_bucket_objects("my-bucket", page=3, per_page=5)
        self.assertEqual(
            [item.name for item in result.items],
            ["file_009.txt", "file_010.txt", "file_011.txt"],
        )

    def test_delete_object(self):
        bucket_name = self.storage.create_bucket("my-bucket")
        bucket = self.storage.client.get_bucket(bucket_name)
        bucket.blob("my_blob.txt")

        self.assertTrue(self.storage.get_bucket_object("my-bucket", "my_blob.txt"))
        self.storage.delete_object("my-bucket", "my_blob.txt")

        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.get_bucket_object("my-bucket", "my_blob.txt")
