import io
from unittest.mock import patch
from urllib.parse import parse_qs, unquote, urlparse

from moto import mock_aws

from hexa.core.test import TestCase
from hexa.files.backends.base import BadRequest
from hexa.files.backends.s3 import S3Storage

REGION = "eu-central-1"
BUCKET = "test-bucket"


def _content_disposition(presigned_url: str) -> str:
    """Return the decoded Content-Disposition header value embedded in a presigned URL."""
    qs = parse_qs(urlparse(presigned_url).query)
    return unquote(qs["response-content-disposition"][0])


class S3StorageTest(TestCase):
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

    def test_bucket_exists_false(self):
        self.assertFalse(self.storage.bucket_exists(BUCKET))

    def test_create_bucket(self):
        self.storage.create_bucket(BUCKET)
        self.assertTrue(self.storage.bucket_exists(BUCKET))

    def test_create_bucket_already_exists(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(self.storage.exceptions.AlreadyExists):
            self.storage.create_bucket(BUCKET)

    def test_delete_bucket(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"data"))
        self.storage.delete_bucket(BUCKET, force=True)
        self.assertFalse(self.storage.bucket_exists(BUCKET))

    def test_delete_bucket_not_empty_raises(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"data"))
        with self.assertRaises(BadRequest):
            self.storage.delete_bucket(BUCKET, force=False)

    def test_save_and_read_object(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "test.txt", io.BytesIO(b"hello world"))
        self.assertEqual(self.storage.read_object(BUCKET, "test.txt"), b"hello world")

    def test_read_object_not_found(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.read_object(BUCKET, "nonexistent.txt")

    def test_create_bucket_folder(self):
        self.storage.create_bucket(BUCKET)
        obj = self.storage.create_bucket_folder(BUCKET, "my-dir")
        self.assertEqual(obj.type, "directory")
        self.assertEqual(obj.name, "my-dir")
        self.assertEqual(obj.key, "my-dir/")

    def test_create_bucket_folder_already_has_trailing_slash(self):
        self.storage.create_bucket(BUCKET)
        obj = self.storage.create_bucket_folder(BUCKET, "my-dir/")
        self.assertEqual(obj.key, "my-dir/")

    def test_get_bucket_object_file(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"content"))
        obj = self.storage.get_bucket_object(BUCKET, "file.txt")
        self.assertEqual(obj.name, "file.txt")
        self.assertEqual(obj.type, "file")
        self.assertEqual(obj.size, 7)

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

    def test_get_bucket_object_not_found(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.get_bucket_object(BUCKET, "nonexistent.txt")

    def test_list_bucket_objects(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file1.txt", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "file2.txt", io.BytesIO(b"b"))
        items = self.storage.list_bucket_objects(BUCKET).items
        self.assertEqual(len(items), 2)
        names = {o.name for o in items}
        self.assertIn("file1.txt", names)
        self.assertIn("file2.txt", names)

    def test_list_bucket_objects_with_prefix(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "dir/file1.txt", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "other/file2.txt", io.BytesIO(b"b"))
        items = self.storage.list_bucket_objects(BUCKET, prefix="dir/").items
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "file1.txt")

    def test_list_bucket_objects_directories_before_files(self):
        self.storage.create_bucket(BUCKET)
        self.storage.create_bucket_folder(BUCKET, "subdir")
        self.storage.save_object(BUCKET, "aaa.txt", io.BytesIO(b"a"))
        items = self.storage.list_bucket_objects(BUCKET).items
        self.assertEqual(items[0].type, "directory")
        self.assertEqual(items[1].type, "file")

    def test_list_bucket_objects_with_match_glob(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "testAAA.txt", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "testAAB.txt", io.BytesIO(b"b"))
        self.storage.save_object(BUCKET, "testABC.txt", io.BytesIO(b"c"))
        items = self.storage.list_bucket_objects(BUCKET, match_glob="*testAA*").items
        self.assertEqual(len(items), 2)
        names = {o.name for o in items}
        self.assertIn("testAAA.txt", names)
        self.assertIn("testAAB.txt", names)

    def test_list_bucket_objects_with_query(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "report_2024.csv", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "summary_2024.csv", io.BytesIO(b"b"))
        self.storage.save_object(BUCKET, "other.txt", io.BytesIO(b"c"))
        items = self.storage.list_bucket_objects(BUCKET, query="2024").items
        self.assertEqual(len(items), 2)
        names = {o.name for o in items}
        self.assertIn("report_2024.csv", names)
        self.assertIn("summary_2024.csv", names)

    def test_list_bucket_objects_query_case_insensitive(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "Report.csv", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "other.txt", io.BytesIO(b"b"))
        items = self.storage.list_bucket_objects(BUCKET, query="report").items
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "Report.csv")

    def test_list_bucket_objects_hidden_files_ignored(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, ".hidden.txt", io.BytesIO(b"h"))
        self.storage.save_object(BUCKET, "visible.txt", io.BytesIO(b"v"))
        items = self.storage.list_bucket_objects(BUCKET).items
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "visible.txt")

    def test_list_bucket_objects_hidden_files_included(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, ".hidden.txt", io.BytesIO(b"h"))
        self.storage.save_object(BUCKET, "visible.txt", io.BytesIO(b"v"))
        items = self.storage.list_bucket_objects(
            BUCKET, ignore_hidden_files=False
        ).items
        self.assertEqual(len(items), 2)

    def test_list_bucket_objects_pagination(self):
        self.storage.create_bucket(BUCKET)
        for i in range(7):
            self.storage.save_object(BUCKET, f"file_{i}.txt", io.BytesIO(b"x"))
        page1 = self.storage.list_bucket_objects(BUCKET, page=1, per_page=3)
        self.assertEqual(len(page1.items), 3)
        self.assertTrue(page1.has_next_page)
        self.assertFalse(page1.has_previous_page)

        page2 = self.storage.list_bucket_objects(BUCKET, page=2, per_page=3)
        self.assertEqual(len(page2.items), 3)
        self.assertTrue(page2.has_next_page)
        self.assertTrue(page2.has_previous_page)

        page3 = self.storage.list_bucket_objects(BUCKET, page=3, per_page=3)
        self.assertEqual(len(page3.items), 1)
        self.assertFalse(page3.has_next_page)

    def test_delete_object_file(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"a"))
        self.storage.delete_object(BUCKET, "file.txt")
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.read_object(BUCKET, "file.txt")

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

    def test_delete_object_not_found(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.delete_object(BUCKET, "nonexistent.txt")

    def test_generate_download_url(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"a"))
        url = self.storage.generate_download_url(
            bucket_name=BUCKET, target_key="file.txt"
        )
        self.assertIsNotNone(url)
        self.assertIn("file.txt", url)

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

    def test_generate_upload_url(self):
        self.storage.create_bucket(BUCKET)
        url, headers = self.storage.generate_upload_url(
            bucket_name=BUCKET, target_key="new.txt"
        )
        self.assertIsNotNone(url)
        self.assertIn("new.txt", url)
        self.assertIsNone(headers)

    def test_generate_upload_url_raise_if_exists(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "existing.txt", io.BytesIO(b"a"))
        with self.assertRaises(self.storage.exceptions.AlreadyExists):
            self.storage.generate_upload_url(
                bucket_name=BUCKET,
                target_key="existing.txt",
                raise_if_exists=True,
            )

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

    def test_delete_bucket_not_found(self):
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.delete_bucket("nonexistent-bucket")

    def test_generate_download_url_force_attachment_non_ascii_filename(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "données.csv", io.BytesIO(b"a"))
        url = self.storage.generate_download_url(
            bucket_name=BUCKET, target_key="données.csv", force_attachment=True
        )
        disposition = _content_disposition(url)
        self.assertIn("attachment", disposition)
        self.assertIn("données.csv", disposition)

    def test_load_bucket_sample_data(self):
        self.storage.create_bucket(BUCKET)
        self.storage.load_bucket_sample_data(BUCKET)
        items = self.storage.list_bucket_objects(
            BUCKET, ignore_hidden_files=False
        ).items
        self.assertGreater(len(items), 0)
