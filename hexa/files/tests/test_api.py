from unittest.mock import patch

import boto3
import botocore
from django.core.exceptions import ValidationError
from django.test import override_settings
from moto import mock_s3

from hexa.core.test import TestCase

from ..api import NotFound, get_storage
from .mocks.mockgcp import backend


class APITestCase:
    def get_client(self):
        return get_storage(self.get_type())

    def to_keys(self, page):
        return [x["key"] for x in page.items]

    def setUp(self):
        if self.get_type() == "gcp":
            from .mocks.client import MockClient

            def create_mock_client(*args, **kwargs):
                return MockClient(backend=backend, *args, **kwargs)

            patcher = patch("hexa.files.gcp.get_storage_client", create_mock_client)
            self.mock_backend = patcher.start()
            self.addCleanup(patcher.stop)

        if self.get_type() == "s3":
            mock = mock_s3()

            self.mock_backend = mock.start()
            self.addCleanup(mock.stop)

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
            self.get_client().delete_bucket(bucket_name=bucket_name, fully=True)

    def test_create_bucket(self):
        self.assertEqual(backend.buckets, {})
        self.get_client().create_bucket("test-bucket")
        self.assertEqual(self.get_client().list_bucket_objects("test-bucket").items, [])

    def test_create_same_bucket(self):
        self.assertEqual(backend.buckets, {})
        self.get_client().create_bucket("test-bucket")
        with self.assertRaises(ValidationError):
            self.get_client().create_bucket("test-bucket")

    def test_list_blobs_empty(self):
        bucket = self.get_client().create_bucket("empty-bucket")
        self.assertEqual(self.get_client().list_bucket_objects(bucket.name).items, [])

    def test_list_blobs(self):
        bucket = self.get_client().create_bucket("not-empty-bucket")
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
            self.to_keys(
                self.get_client().list_bucket_objects(bucket.name, page=1, per_page=2)
            ),
            [
                "folder/",
                "other_file.md",
            ],
        )

    def test_list_blobs_with_query(self):
        bucket = self.get_client().create_bucket("not-empty-bucket")
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
            "file.md",
            size=1,
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
                for x in self.get_client()
                .list_bucket_objects(bucket.name, page=1, per_page=10, query="readme")
                .items
            ],
            [
                "readme.md",
            ],
        )

        self.assertEqual(
            [
                x["key"]
                for x in self.get_client()
                .list_bucket_objects(bucket.name, page=1, per_page=10, query="file")
                .items
            ],
            ["file.md", "other_file.md"],
        )
        self.assertEqual(
            [
                x["key"]
                for x in self.get_client()
                .list_bucket_objects(bucket.name, page=2, per_page=10, query="file")
                .items
            ],
            [],
        )

    def test_list_hide_hidden_files(self):
        bucket = self.get_client().create_bucket("bucket")
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
            self.to_keys(
                self.get_client().list_bucket_objects(bucket.name, page=1, per_page=10)
            ),
            [
                "test.txt",
            ],
        )

        self.assertEqual(
            self.to_keys(
                self.get_client().list_bucket_objects(
                    bucket.name, page=1, per_page=10, ignore_hidden_files=False
                )
            ),
            [".git/", ".gitconfig", ".gitignore", "test.txt"],
        )

    def test_list_blobs_with_prefix(self):
        bucket = self.get_client().create_bucket("bucket")
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
            self.to_keys(
                self.get_client().list_bucket_objects(
                    bucket.name, page=1, per_page=10, prefix="dir/"
                )
            ),
            [
                "dir/b/",
                "dir/readme.md",
            ],
        )

    def test_list_blobs_pagination(self):
        bucket = self.get_client().create_bucket("my-bucket")
        for i in range(0, 12):
            bucket.blob(f"test_{i}.txt", size=(123 * i), content_type="text/plain")

        res = self.get_client().list_bucket_objects(bucket.name, page=1, per_page=10)

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

        res = self.get_client().list_bucket_objects(bucket.name, page=1, per_page=20)
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

        res = self.get_client().list_bucket_objects(bucket.name, page=2, per_page=10)
        self.assertEqual(self.to_keys(res), ["test_8.txt", "test_9.txt"])
        self.assertFalse(res.has_next_page)
        self.assertTrue(res.has_previous_page)
        self.assertEqual(res.page_number, 2)

        res = self.get_client().list_bucket_objects(bucket.name, page=2, per_page=5)
        self.assertEqual(
            self.to_keys(res),
            ["test_3.txt", "test_4.txt", "test_5.txt", "test_6.txt", "test_7.txt"],
        )

        self.assertTrue(res.has_next_page)
        self.assertTrue(res.has_previous_page)
        self.assertEqual(res.page_number, 2)

    def test_delete_object_working(self):
        bucket = self.get_client().create_bucket("bucket")
        bucket.blob(
            "test.txt",
            size=123,
            content_type="text/plain",
        )
        res = self.get_client().list_bucket_objects("bucket")
        self.assertEqual(self.to_keys(res), ["test.txt"])

        self.get_client().delete_object(bucket_name=bucket.name, file_name="test.txt")
        res = self.get_client().list_bucket_objects("bucket")

        self.assertEqual(self.to_keys(res), [])

    def test_delete_object_non_existing(self):
        bucket = self.get_client().create_bucket("bucket")
        with self.assertRaises(NotFound):
            self.get_client().delete_object(
                bucket_name=bucket.name, file_name="test.txt"
            )

    def test_generate_download_url(self):
        self.get_client().create_bucket("bucket")
        url = self.get_client().generate_download_url("bucket", "demo.txt")
        assert "demo.txt" in url, f"Expected to be in '{url}'"

    def test_generate_upload_url(self):
        self.get_client().create_bucket("bucket")
        url = self.get_client().generate_upload_url("bucket", "demo.txt")
        assert "demo.txt" in url, f"Expected to be in '{url}'"

    def test_generate_upload_url_raise_existing(self):
        bucket = self.get_client().create_bucket("bucket")
        bucket.blob(
            "demo.txt",
            size=123,
            content_type="text/plain",
        )
        with self.assertRaises(ValidationError):
            self.get_client().generate_upload_url(
                bucket_name="bucket", target_key="demo.txt", raise_if_exists=True
            )


class OnlyGCP:
    @override_settings(WORKSPACE_BUCKET_VERSIONING_ENABLED="true")
    def test_create_bucket_configuration(self):
        bucket = self.get_client().create_bucket("bucket")

        self.assertEqual(bucket.versioning_enabled, True)
        self.assertEqual(
            bucket.lifecycle_rules,
            [
                {
                    "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
                    "condition": {"age": 30},
                },
                {
                    "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
                    "condition": {"age": 90},
                },
                {
                    "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
                    "condition": {"age": 365},
                },
                {
                    "action": {"type": "Delete"},
                    "condition": {"isLive": False, "numNewerVersions": 3},
                },
            ],
        )
        self.assertEqual(bucket.storage_class, "STANDARD")


class OnlyS3:
    def test_generate_upload_url_raise_existing_dont_raise(self):
        self.get_client().delete_bucket("bucket")
        self.get_client().create_bucket("bucket")
        url = self.get_client().generate_upload_url(
            bucket_name="bucket", target_key="demo.txt", raise_if_exists=True
        )

        assert "demo.txt" in url, f"Expected to be in '{url}'"

    def test_load_bucket_sample_data(self):
        self.get_client().create_bucket("bucket")
        self.get_client().load_bucket_sample_data(bucket_name="bucket")
        res = self.get_client().list_bucket_objects("bucket")

        self.assertEqual(
            self.to_keys(res), ["README.MD", "covid_data.csv", "demo.ipynb"]
        )

    def test_create_bucket_folder(self):
        self.get_client().create_bucket("bucket")
        self.assertEqual(self.get_client().list_bucket_objects("bucket").items, [])
        self.get_client().create_bucket_folder(bucket_name="bucket", folder_key="demo")
        self.assertEqual(
            self.to_keys(self.get_client().list_bucket_objects("bucket")),
            ["demo/"],
        )

    def test_generate_client_upload_url(self):
        self.get_client().create_bucket("bucket")

        url = self.get_client().generate_upload_url(
            bucket_name="bucket", target_key="demo.txt"
        )
        self.assertFalse(url.startswith("https://custom-s3.local"))

        with override_settings(
            WORKSPACE_STORAGE_ENGINE_AWS_PUBLIC_ENDPOINT_URL="https://custom-s3.local"
        ):
            url = self.get_client().generate_upload_url(
                bucket_name="bucket", target_key="demo.txt"
            )
            self.assertTrue(url.startswith("https://custom-s3.local"))

    def test_generate_client_download_url(self):
        bucket = self.get_client().create_bucket("bucket")
        bucket.blob("demo.txt", size=123, content_type="text/plain")

        url = self.get_client().generate_download_url("bucket", "demo.txt")
        self.assertFalse(url.startswith("https://custom-s3.local"))

        with override_settings(
            WORKSPACE_STORAGE_ENGINE_AWS_PUBLIC_ENDPOINT_URL="https://custom-s3.local"
        ):
            url = self.get_client().generate_download_url("bucket", "demo.txt")
            self.assertTrue(url.startswith("https://custom-s3.local"))


class OnlyOnline:
    def test_short_lived_downscoped_access_token(self):
        # TODO make that test work for gcp and s3
        bucket = self.get_client().create_bucket("bucket")
        for i in range(0, 2):
            bucket.blob(
                f"test_{i}.txt",
                size=123 * i,
                content_type="text/plain",
            )

        bucket = self.get_client().create_bucket("test-bucket")

        for i in range(0, 2):
            bucket.blob(
                f"test_{i}.txt",
                size=123 * i,
                content_type="text/plain",
            )

        token = self.get_client().get_short_lived_downscoped_access_token("bucket")

        env_vars = self.get_client().get_token_as_env_variables(token[0])

        if self.get_type() == "s3":
            self.assertEqual(
                list(env_vars.keys()),
                [
                    "AWS_ACCESS_KEY_ID",
                    "AWS_SECRET_ACCESS_KEY",
                    "AWS_ENDPOINT_URL",
                    "AWS_SESSION_TOKEN",
                    "AWS_S3_FUSE_CONFIG",
                ],
            )

            # create a s3 client with the downscoped token
            s3 = boto3.client("s3", **token[0])

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


# MOTO the lib to mock s3 doesn't work when you set and endpoint url
@override_settings(WORKSPACE_STORAGE_ENGINE_AWS_ENDPOINT_URL=None)
class APIS3TestCase(APITestCase, OnlyS3, TestCase):
    def get_type(self):
        return "s3"


class APIGcpTestCase(APITestCase, OnlyGCP, TestCase):
    def get_type(self):
        return "gcp"
