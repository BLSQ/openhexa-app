import io
from unittest.mock import patch
from urllib.parse import parse_qs, unquote, urlparse

from botocore.exceptions import ClientError
from moto import mock_aws

from hexa.core.test import TestCase
from hexa.files.backends.s3 import S3Storage
from hexa.files.tests.backends.base import StorageTestMixin

REGION = "eu-central-1"
BUCKET = "test-bucket"


def _content_disposition(presigned_url: str) -> str:
    """Return the decoded Content-Disposition header value embedded in a presigned URL."""
    qs = parse_qs(urlparse(presigned_url).query)
    return unquote(qs["response-content-disposition"][0])


class S3StorageTest(StorageTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.mock = mock_aws()
        self.mock.start()
        self.storage = S3Storage(
            access_key_id="fake-access-key",
            secret_access_key="fake-secret-key",
            region=REGION,
        )

    def tearDown(self):
        self.mock.stop()
        super().tearDown()

    def test_create_bucket_sets_cors(self):
        self.storage.create_bucket(BUCKET)
        cors = self.storage.client.get_bucket_cors(Bucket=BUCKET)
        self.assertEqual(len(cors["CORSRules"]), 1)
        rule = cors["CORSRules"][0]
        self.assertEqual(rule["AllowedOrigins"], ["*"])
        self.assertEqual(
            sorted(rule["AllowedMethods"]), ["DELETE", "GET", "HEAD", "POST", "PUT"]
        )
        self.assertEqual(rule["AllowedHeaders"], ["*"])
        self.assertIn("ETag", rule["ExposeHeaders"])
        self.assertEqual(rule["MaxAgeSeconds"], 3600)

    def test_create_bucket_enables_versioning(self):
        storage = S3Storage(
            access_key_id="fake-access-key",
            secret_access_key="fake-secret-key",
            region=REGION,
            enable_versioning=True,
        )
        storage.create_bucket(BUCKET)
        versioning = storage.client.get_bucket_versioning(Bucket=BUCKET)
        self.assertEqual(versioning.get("Status"), "Enabled")

    def test_create_bucket_versioning_disabled(self):
        self.storage.create_bucket(BUCKET)
        versioning = self.storage.client.get_bucket_versioning(Bucket=BUCKET)
        self.assertNotIn("Status", versioning)

    def test_create_bucket_sets_lifecycle(self):
        self.storage.create_bucket(BUCKET)
        lifecycle = self.storage.client.get_bucket_lifecycle_configuration(
            Bucket=BUCKET
        )
        rules = {rule["ID"]: rule for rule in lifecycle["Rules"]}
        self.assertEqual(
            rules["transition-storage-classes"]["Transitions"],
            [
                {"Days": 30, "StorageClass": "STANDARD_IA"},
                {"Days": 90, "StorageClass": "GLACIER_IR"},
                {"Days": 365, "StorageClass": "DEEP_ARCHIVE"},
            ],
        )
        # moto accepts NewerNoncurrentVersions on put but does not return it on get
        self.assertEqual(
            rules["cleanup-noncurrent-versions"]["NoncurrentVersionExpiration"][
                "NoncurrentDays"
            ],
            1,
        )
        self.assertEqual(
            rules["cleanup-incomplete-uploads"]["AbortIncompleteMultipartUpload"],
            {"DaysAfterInitiation": 7},
        )

    def test_create_bucket_sets_labels(self):
        self.storage.create_bucket(BUCKET, labels={"hexa_workspace": "test"})
        tagging = self.storage.client.get_bucket_tagging(Bucket=BUCKET)
        self.assertEqual(
            tagging["TagSet"], [{"Key": "hexa_workspace", "Value": "test"}]
        )

    def test_create_bucket_without_labels_sets_no_tags(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(ClientError):
            self.storage.client.get_bucket_tagging(Bucket=BUCKET)

    def test_create_bucket_lifecycle_falls_back_without_transitions(self):
        # MinIO-like stores reject transition rules with InvalidStorageClass;
        # the cleanup rules must still be applied.
        invalid_storage_class = ClientError(
            {
                "Error": {
                    "Code": "InvalidStorageClass",
                    "Message": "Invalid storage class.",
                }
            },
            "PutBucketLifecycleConfiguration",
        )
        original = self.storage.client.put_bucket_lifecycle_configuration
        calls = []

        def fail_on_transitions(**kwargs):
            calls.append(kwargs)
            if any(
                "Transitions" in rule
                for rule in kwargs["LifecycleConfiguration"]["Rules"]
            ):
                raise invalid_storage_class
            return original(**kwargs)

        with patch.object(
            self.storage.client,
            "put_bucket_lifecycle_configuration",
            side_effect=fail_on_transitions,
        ), patch("sentry_sdk.capture_exception") as mock_capture:
            self.storage.create_bucket(BUCKET)

        mock_capture.assert_called_once()
        self.assertEqual(len(calls), 2)
        lifecycle = self.storage.client.get_bucket_lifecycle_configuration(
            Bucket=BUCKET
        )
        rule_ids = {rule["ID"] for rule in lifecycle["Rules"]}
        self.assertEqual(
            rule_ids, {"cleanup-noncurrent-versions", "cleanup-incomplete-uploads"}
        )

    def test_create_bucket_tolerates_not_implemented(self):
        # S3-compatible stores like MinIO do not implement every bucket
        # configuration API; creation must still succeed.
        not_implemented = ClientError(
            {"Error": {"Code": "NotImplemented", "Message": "not supported"}},
            "PutBucketCors",
        )
        with patch.object(
            self.storage.client, "put_bucket_cors", side_effect=not_implemented
        ), patch("sentry_sdk.capture_exception") as mock_capture:
            self.storage.create_bucket(BUCKET)

        mock_capture.assert_called_once()
        self.assertTrue(self.storage.bucket_exists(BUCKET))

    def test_create_bucket_config_error_raises(self):
        access_denied = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "denied"}},
            "PutBucketCors",
        )
        with patch.object(
            self.storage.client, "put_bucket_cors", side_effect=access_denied
        ):
            with self.assertRaises(ClientError):
                self.storage.create_bucket(BUCKET)

    def test_delete_bucket(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"data"))
        self.storage.delete_bucket(BUCKET, force=True)
        self.assertFalse(self.storage.bucket_exists(BUCKET))

    def test_delete_bucket_not_empty_raises(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"data"))
        with self.assertRaises(self.storage.exceptions.BadRequest):
            self.storage.delete_bucket(BUCKET, force=False)

    def test_create_bucket_folder_already_has_trailing_slash(self):
        self.storage.create_bucket(BUCKET)
        obj = self.storage.create_bucket_folder(BUCKET, "my-dir/")
        self.assertEqual(obj.key, "my-dir/")

    def test_get_bucket_object_directory(self):
        self.storage.create_bucket(BUCKET)
        self.storage.create_bucket_folder(BUCKET, "my-dir")
        obj = self.storage.get_bucket_object(BUCKET, "my-dir")
        self.assertEqual(obj.name, "my-dir")
        self.assertEqual(obj.type, "directory")

    def test_get_bucket_object_directory_with_trailing_slash(self):
        self.storage.create_bucket(BUCKET)
        self.storage.create_bucket_folder(BUCKET, "my-dir")
        obj = self.storage.get_bucket_object(BUCKET, "my-dir/")
        self.assertEqual(obj.name, "my-dir")
        self.assertEqual(obj.type, "directory")
        self.assertEqual(obj.key, "my-dir/")

    def test_list_bucket_objects_directories_before_files(self):
        self.storage.create_bucket(BUCKET)
        self.storage.create_bucket_folder(BUCKET, "subdir")
        self.storage.save_object(BUCKET, "aaa.txt", io.BytesIO(b"a"))
        items = self.storage.list_bucket_objects(BUCKET).items
        self.assertEqual(items[0].type, "directory")
        self.assertEqual(items[1].type, "file")

    def test_delete_object_directory(self):
        self.storage.create_bucket(BUCKET)
        self.storage.create_bucket_folder(BUCKET, "my-dir")
        self.storage.save_object(BUCKET, "my-dir/file1.txt", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "my-dir/file2.txt", io.BytesIO(b"b"))
        self.storage.delete_object(BUCKET, "my-dir")
        items = self.storage.list_bucket_objects(BUCKET).items
        self.assertEqual(len(items), 0)
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.get_bucket_object(BUCKET, "my-dir")

    def test_generate_download_url_force_attachment(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "report.csv", io.BytesIO(b"a,b"))
        url = self.storage.generate_download_url(
            bucket_name=BUCKET, target_key="report.csv", force_attachment=True
        )
        self.assertIn("attachment", url)
        self.assertIn("report.csv", url)

    def test_generate_download_url_force_attachment_special_chars(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "my report (2024).csv", io.BytesIO(b"a,b"))
        url = self.storage.generate_download_url(
            bucket_name=BUCKET,
            target_key="my report (2024).csv",
            force_attachment=True,
        )
        disposition = _content_disposition(url)
        self.assertIn("attachment", disposition)
        self.assertIn("my report (2024).csv", disposition)
        self.assertNotIn("%20", disposition)

    def test_generate_download_url_force_attachment_no_double_encoding(self):
        # Regression test: quote() was previously applied to the filename before passing
        # it to boto3, which double-encodes it. Browsers then display "my%20file.csv"
        # instead of "my file.csv" as the suggested filename.
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "my file.csv", io.BytesIO(b"a"))
        url = self.storage.generate_download_url(
            bucket_name=BUCKET, target_key="my file.csv", force_attachment=True
        )
        disposition = _content_disposition(url)
        self.assertIn("my file.csv", disposition)
        self.assertNotIn("%20", disposition)

    def test_generate_download_url_force_attachment_non_ascii_filename(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "données.csv", io.BytesIO(b"a"))
        url = self.storage.generate_download_url(
            bucket_name=BUCKET, target_key="données.csv", force_attachment=True
        )
        disposition = _content_disposition(url)
        self.assertIn("attachment", disposition)
        self.assertIn("données.csv", disposition)

    def test_get_bucket_mount_config_static_credentials(self):
        self.storage.create_bucket(BUCKET)
        config = self.storage.get_bucket_mount_config(BUCKET)
        self.assertEqual(config["WORKSPACE_STORAGE_ENGINE_S3_BUCKET_NAME"], BUCKET)
        self.assertEqual(
            config["WORKSPACE_STORAGE_ENGINE_S3_ACCESS_KEY_ID"], "fake-access-key"
        )
        self.assertEqual(
            config["WORKSPACE_STORAGE_ENGINE_S3_SECRET_ACCESS_KEY"], "fake-secret-key"
        )
        self.assertEqual(config["WORKSPACE_STORAGE_ENGINE_S3_REGION_NAME"], REGION)
        self.assertNotIn("WORKSPACE_STORAGE_ENGINE_S3_SESSION_TOKEN", config)

    def test_get_bucket_mount_config_sts_credentials(self):
        storage_with_role = S3Storage(
            access_key_id="fake-access-key",
            secret_access_key="fake-secret-key",
            region=REGION,
            role_arn="arn:aws:iam::123456789012:role/test-role",
        )
        mock_creds = {
            "AccessKeyId": "STS-ACCESS-KEY",
            "SecretAccessKey": "STS-SECRET-KEY",
            "SessionToken": "STS-SESSION-TOKEN",
        }
        with patch.object(
            storage_with_role, "_assume_role_credentials", return_value=mock_creds
        ):
            config = storage_with_role.get_bucket_mount_config(BUCKET)

        self.assertEqual(
            config["WORKSPACE_STORAGE_ENGINE_S3_ACCESS_KEY_ID"], "STS-ACCESS-KEY"
        )
        self.assertEqual(
            config["WORKSPACE_STORAGE_ENGINE_S3_SECRET_ACCESS_KEY"], "STS-SECRET-KEY"
        )
        self.assertEqual(
            config["WORKSPACE_STORAGE_ENGINE_S3_SESSION_TOKEN"], "STS-SESSION-TOKEN"
        )

    def test_get_bucket_mount_config_sts_falls_back_to_static(self):
        storage_with_role = S3Storage(
            access_key_id="fake-access-key",
            secret_access_key="fake-secret-key",
            region=REGION,
            role_arn="arn:aws:iam::123456789012:role/test-role",
        )
        with patch.object(
            storage_with_role,
            "_assume_role_credentials",
            side_effect=Exception("STS unavailable"),
        ), patch("sentry_sdk.capture_exception") as mock_capture:
            config = storage_with_role.get_bucket_mount_config(BUCKET)

        mock_capture.assert_called_once()
        self.assertEqual(
            config["WORKSPACE_STORAGE_ENGINE_S3_ACCESS_KEY_ID"], "fake-access-key"
        )
        self.assertNotIn("WORKSPACE_STORAGE_ENGINE_S3_SESSION_TOKEN", config)
