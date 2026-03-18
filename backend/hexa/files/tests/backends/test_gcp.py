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
        """Subdirectories split across GCP API pages appear on their respective pages."""
        bucket_name = self.storage.create_bucket("my-bucket")
        bucket = self.storage_client.get_bucket(bucket_name)

        bucket.blob("aaa/").upload_from_string(b"")
        bucket.blob("bbb/").upload_from_string(b"")
        for i in range(8):
            bucket.blob(f"file_{i:02d}.txt").upload_from_string(b"data")
        bucket.blob("zzz/").upload_from_string(b"")

        page1 = self.storage.list_bucket_objects("my-bucket", page=1, per_page=5)
        page2 = self.storage.list_bucket_objects("my-bucket", page=2, per_page=5)
        page3 = self.storage.list_bucket_objects("my-bucket", page=3, per_page=5)

        all_items = page1.items + page2.items + page3.items
        all_names = [item.name for item in all_items]
        directory_names = [item.name for item in all_items if item.type == "directory"]

        self.assertIn("aaa", directory_names)
        self.assertIn("bbb", directory_names)
        self.assertIn("zzz", directory_names)
        self.assertEqual(len(all_names), 11)

    def test_delete_object(self):
        bucket_name = self.storage.create_bucket("my-bucket")
        bucket = self.storage.client.get_bucket(bucket_name)
        bucket.blob("my_blob.txt")

        self.assertTrue(self.storage.get_bucket_object("my-bucket", "my_blob.txt"))
        self.storage.delete_object("my-bucket", "my_blob.txt")

        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.get_bucket_object("my-bucket", "my_blob.txt")
