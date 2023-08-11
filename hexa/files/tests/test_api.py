from django.core.exceptions import ValidationError

from hexa.core.test import TestCase

from ..api import create_bucket, list_bucket_objects
from .mocks.mockgcp import backend


class APITestCase(TestCase):
    def setUp(self):
        backend.reset()

    @backend.mock_storage
    def test_create_bucket(self):
        self.assertEqual(backend.buckets, {})
        create_bucket("test-bucket")
        self.assertEqual(list(backend.buckets.keys()), ["test-bucket"])

    @backend.mock_storage
    def test_create_same_bucket(self):
        self.assertEqual(backend.buckets, {})
        create_bucket("test-bucket")
        with self.assertRaises(ValidationError):
            create_bucket("test-bucket")

    @backend.mock_storage
    def test_list_blobs_empty(self):
        bucket = create_bucket("empty-bucket")
        self.assertEqual(list_bucket_objects(bucket.name).items, [])

    @backend.mock_storage
    def test_list_blobs(self):
        bucket = create_bucket("not-empty-bucket")
        bucket.blob(
            "test.txt",
            size=123,
            content_type="text/plain",
        )
        bucket.blob(
            "readme.md",
            size=2103,
            content_type="text/plain",
        )
        bucket.blob(
            "other_file.md",
            size=2102,
            content_type="text/plain",
        )
        bucket.blob("folder/", size=0)
        bucket.blob(
            "folder/readme.md",
            size=1,
            content_type="text/plain",
        )
        self.assertEqual(
            [
                x["key"]
                for x in list_bucket_objects(bucket.name, page=1, per_page=2).items
            ],
            [
                "folder/",
                "other_file.md",
            ],
        )

    @backend.mock_storage
    def test_list_hide_hidden_files(self):
        bucket = create_bucket("bucket")
        bucket.blob(
            "test.txt",
            size=123,
            content_type="text/plain",
        )
        bucket.blob(
            ".gitconfig",
            size=2103,
            content_type="text/plain",
        )
        bucket.blob(
            ".gitignore",
            size=2102,
            content_type="text/plain",
        )
        bucket.blob(".git/", size=0)
        bucket.blob(".git/config", size=1, content_type="text/plain")

        self.assertEqual(
            [
                x["key"]
                for x in list_bucket_objects(bucket.name, page=1, per_page=10).items
            ],
            [
                "test.txt",
            ],
        )

        self.assertEqual(
            [
                x["key"]
                for x in list_bucket_objects(
                    bucket.name, page=1, per_page=10, ignore_hidden_files=False
                ).items
            ],
            [".git/", ".gitconfig", ".gitignore", "test.txt"],
        )

    @backend.mock_storage
    def test_list_blobs_with_prefix(self):
        bucket = create_bucket("bucket")
        bucket.blob(
            "test.txt",
            size=123,
            content_type="text/plain",
        )
        bucket.blob(
            "dir/",
            size=0,
        )
        bucket.blob(
            "dir/readme.md",
            size=2102,
            content_type="text/plain",
        )
        bucket.blob("dir/b/", size=0)
        bucket.blob("dir/b/image.jpg", size=1, content_type="image/jpeg")
        bucket.blob("other_dir/", size=0)

        self.assertEqual(
            [
                x["key"]
                for x in list_bucket_objects(
                    bucket.name, page=1, per_page=10, prefix="dir/"
                ).items
            ],
            [
                "dir/b/",
                "dir/readme.md",
            ],
        )

    @backend.mock_storage
    def test_list_blobs_pagination(self):
        bucket = create_bucket("my_bucket")
        for i in range(0, 12):
            bucket.blob(
                f"test_{i}.txt",
                size=123 * i,
                content_type="text/plain",
            )

        res = list_bucket_objects(bucket.name, page=1, per_page=10)
        self.assertTrue(res.has_next_page)
        self.assertFalse(res.has_previous_page)
        self.assertEqual(res.page_number, 1)

        res = list_bucket_objects(bucket.name, page=1, per_page=20)
        self.assertFalse(res.has_next_page)

        res = list_bucket_objects(bucket.name, page=2, per_page=10)
        self.assertFalse(res.has_next_page)
        self.assertTrue(res.has_previous_page)
        self.assertEqual(res.page_number, 2)

        res = list_bucket_objects(bucket.name, page=2, per_page=5)
        self.assertTrue(res.has_next_page)
        self.assertTrue(res.has_previous_page)
        self.assertEqual(res.page_number, 2)
