from django.core.exceptions import ValidationError

from hexa.core.test import TestCase

from ..api import create_bucket, list_bucket_objects
from .mocks.mockgcp import backend


class APITestCase(TestCase):
    @classmethod
    @backend.mock_storage
    def setUpTestData(cls):
        backend.reset()

    @backend.mock_storage
    def test_create_bucket(self):
        self.assertTrue(backend.buckets == {})
        create_bucket("test-bucket")
        self.assertEqual(list(backend.buckets.keys()), ["test-bucket"])

    @backend.mock_storage
    def test_create_same_bucket(self):
        self.assertTrue(backend.buckets == {})
        create_bucket("test-bucket")
        with self.assertRaises(ValidationError):
            create_bucket("test-bucket")

    @backend.mock_storage
    def test_list_blobs_empty(self):
        bucket = create_bucket("empty-bucket")
        self.assertEqual(list_bucket_objects(bucket.name).items, [])
