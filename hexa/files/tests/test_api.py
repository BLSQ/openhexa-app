from django.core.exceptions import ValidationError
import boto3
import botocore
from hexa.core.test import TestCase

from ..api import (
    mode,
    NotFound,
    create_bucket,
    list_bucket_objects,
    create_bucket_folder,
    get_client,
    get_short_lived_downscoped_access_token,
)
from .mocks.mockgcp import backend


class APITestCase(TestCase):
    def to_keys(self, page):
        return [x["key"] for x in page.items]

    def setUp(self):
        backend.reset()
        # since I call a real minio, I delete the content and bucket upfront
        buckets = [
            "my_bucket",
            "my-bucket",
            "test-bucket",
            "empty-bucket",
            "not-empty-bucket",
            "bucket",
        ]
        for bucket_name in buckets:
            get_client().delete_bucket(bucket_name=bucket_name, fully=True)

    @backend.mock_s3_storage
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
        bucket = create_bucket("my-bucket")
        for i in range(0, 12):
            bucket.blob(f"test_{i}.txt", size=(123 * i), content_type="text/plain")

        res = list_bucket_objects(bucket.name, page=1, per_page=10)

        self.assertEqual(
            self.to_keys(res),
            [
                "test_0.txt",
                "test_1.txt",
                "test_10.txt",
                "test_11.txt",
                "test_2.txt",
                "test_3.txt",
                "test_4.txt",
                "test_5.txt",
                "test_6.txt",
                "test_7.txt",
            ],
        )

        self.assertTrue(res.has_next_page)
        self.assertFalse(res.has_previous_page)
        self.assertEqual(res.page_number, 1)

        res = list_bucket_objects(bucket.name, page=1, per_page=20)
        self.assertEqual(
            self.to_keys(res),
            [
                "test_0.txt",
                "test_1.txt",
                "test_10.txt",
                "test_11.txt",
                "test_2.txt",
                "test_3.txt",
                "test_4.txt",
                "test_5.txt",
                "test_6.txt",
                "test_7.txt",
                "test_8.txt",
                "test_9.txt",
            ],
        )
        self.assertFalse(res.has_next_page)

        res = list_bucket_objects(bucket.name, page=2, per_page=10)
        self.assertEqual(self.to_keys(res), ["test_8.txt", "test_9.txt"])
        self.assertFalse(res.has_next_page)
        self.assertTrue(res.has_previous_page)
        self.assertEqual(res.page_number, 2)

        res = list_bucket_objects(bucket.name, page=2, per_page=5)
        self.assertEqual(
            self.to_keys(res),
            ["test_3.txt", "test_4.txt", "test_5.txt", "test_6.txt", "test_7.txt"],
        )

        self.assertTrue(res.has_next_page)
        self.assertTrue(res.has_previous_page)
        self.assertEqual(res.page_number, 2)

    @backend.mock_storage
    def test_create_bucket_folder(self):
        create_bucket("bucket")
        self.assertEqual(list_bucket_objects("bucket").items, [])
        create_bucket_folder(bucket_name="bucket", folder_key="demo")
        
        self.assertEqual(
            list_bucket_objects("bucket").items,
            [
                {
                    "key": "demo/",
                    "name": "demo",
                    "path": "bucket/demo/",
                    "size": 0,
                    "type": "directory",
                }
            ],
        )

    @backend.mock_storage
    def test_short_lived_downscoped_access_token(self):
        # TODO make that test work for gcp and s3
        bucket = create_bucket("bucket")
        for i in range(0, 2):
            bucket.blob(
                f"test_{i}.txt",
                size=123 * i,
                content_type="text/plain",
            )

        bucket = create_bucket("test-bucket")

        for i in range(0, 2):
            bucket.blob(
                f"test_{i}.txt",
                size=123 * i,
                content_type="text/plain",
            )

        connection_infos, expires_in = get_short_lived_downscoped_access_token("bucket")
        if mode == "s3":
            # create a s3 client with the downscoped token 
            s3 = boto3.client("s3", **connection_infos)

            objects = s3.list_objects(Bucket="bucket")
            print(objects)
            self.assertEqual(
                [x["Key"] for x in objects["Contents"]],
                ["test_0.txt", "test_1.txt"],
            )
            # TODO unified exception ?
            with self.assertRaisesMessage(
                botocore.exceptions.ClientError,
                "An error occurred (AccessDenied) when calling the ListObjects operation: Access Denied.",
            ):
                # should blow up not allowed on that bucket
                objects = s3.list_objects(Bucket="test-bucket")

            with self.assertRaisesMessage(
                botocore.exceptions.ClientError,
                "An error occurred (AccessDenied) when calling the CreateBucket operation: Access Denied.",
            ):
                # should blow up not allowed to create new bucket
                s3.create_bucket(Bucket="not-empty-bucket")

    def test_delete_object_working(self):

        bucket = create_bucket("bucket")
        bucket.blob(
            "test.txt",
            size=123,
            content_type="text/plain",
        )
        res = list_bucket_objects("bucket")
        self.assertEqual(self.to_keys(res), ["test.txt"])

        get_client().delete_object(bucket_name=bucket.name, file_name="test.txt")
        res = list_bucket_objects("bucket")

        self.assertEqual(self.to_keys(res), [])

    def test_delete_object_non_existing(self):

        bucket = create_bucket("bucket")
        with self.assertRaises(NotFound):
            get_client().delete_object(bucket_name=bucket.name, file_name="test.txt")

