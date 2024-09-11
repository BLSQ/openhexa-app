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

    def test_delete_object(self):
        bucket_name = self.storage.create_bucket("my-bucket")
        bucket = self.storage.client.get_bucket(bucket_name)
        bucket.blob("my_blob.txt")

        self.assertTrue(self.storage.get_bucket_object("my-bucket", "my_blob.txt"))
        self.storage.delete_object("my-bucket", "my_blob.txt")

        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.get_bucket_object("my-bucket", "my_blob.txt")
