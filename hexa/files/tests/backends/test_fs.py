import os
import shutil
from io import BytesIO
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from hexa.core.test import TestCase
from hexa.files.backends.fs import FileSystemStorage


class FileSystemStorageTest(TestCase):
    storage = None

    def setUp(self):
        super().setUp()
        self.data_directory = Path(mkdtemp())
        self.storage = FileSystemStorage(
            data_dir=self.data_directory,
        )

    def tearDown(self) -> None:
        super().tearDown()
        shutil.rmtree(self.data_directory)

    def test_create_bucket(self):
        self.storage.create_bucket("test")
        self.assertTrue(self.storage.exists("test"))
        self.assertTrue(os.path.lexists(self.storage.path("test")))
        self.assertEqual(self.storage.path("test"), self.data_directory / "test")

    def test_suspicious_create_bucket(self):
        for path in ["../test", "/test", "../../test", "dir/subdir"]:
            with self.assertRaises(self.storage.exceptions.SuspiciousFileOperation):
                self.storage.create_bucket(path)

    def test_path(self):
        self.assertEqual(
            self.storage.path("my-dir/my-subdir/my-file.png"),
            self.data_directory / "my-dir/my-subdir/my-file.png",
        )
        self.assertEqual(
            self.storage.path("my-dir/../my-dir/my-subdir/my-file.png"),
            self.data_directory / "my-dir/my-subdir/my-file.png",
        )

        with self.assertRaises(self.storage.exceptions.SuspiciousFileOperation):
            self.storage.path("../my-dir/my-subdir/my-file.png")

    def test_create_bucket_folder(self):
        self.storage.create_bucket("my-bucket")
        self.storage.create_bucket("my-second-bucket")
        self.storage.create_bucket_folder("my-bucket", "my-dir")

        self.assertTrue(self.storage.exists("my-bucket/my-dir"))
        self.assertTrue(os.path.lexists(self.storage.path("my-bucket/my-dir")))

        self.assertTrue(self.storage.exists("my-second-bucket"))
        self.assertFalse(self.storage.exists("my-second-bucket/my-dir"))

        with self.assertRaises(self.storage.exceptions.SuspiciousFileOperation):
            self.storage.create_bucket_folder(
                "my-bucket", "../my-second-bucket/my-second-dir"
            )
        self.assertFalse(
            os.path.lexists(self.storage.path("my-second-bucket/my-second-dir"))
        )
        self.assertFalse(
            os.path.lexists(self.data_directory / "my-bucket/my-second-dir")
        )

    def test_valid_filenames(self):
        self.storage.create_bucket("default-bucket")
        dir_obj = self.storage.create_bucket_folder("default-bucket", "éà_?_d 1")
        self.assertEqual(dir_obj.name, "éà__d_1")

    def test_save_object(self):
        self.storage.create_bucket("default-bucket")
        self.storage.save_object("default-bucket", "file.txt", b"Hello, world!")

        self.assertTrue((self.data_directory / "default-bucket/file.txt").exists())
        self.assertEqual(
            open(self.data_directory / "default-bucket/file.txt").read(),
            "Hello, world!",
        )

    def test_deep_save_object(self):
        self.storage.create_bucket("default-bucket")
        self.storage.save_object(
            "default-bucket", "dir1/dir2/file.txt", b"Hello, world!"
        )
        self.assertTrue(
            (self.data_directory / "default-bucket/dir1/dir2/file.txt").exists()
        )

        self.storage.save_object("default-bucket", "dir1/file2.txt", b"Hello, world!")
        self.assertTrue(
            (self.data_directory / "default-bucket/dir1/file2.txt").exists()
        )

    def test_overwrite_object(self):
        self.storage.create_bucket("default-bucket")
        self.storage.save_object("default-bucket", "file.txt", b"Hello, world!")

        self.assertTrue((self.data_directory / "default-bucket/file.txt").exists())
        self.assertEqual(
            open(self.data_directory / "default-bucket/file.txt").read(),
            "Hello, world!",
        )

        # Overwrite the file
        self.storage.save_object("default-bucket", "file.txt", b"OVERWRITTEN")
        self.assertEqual(
            open(self.data_directory / "default-bucket/file.txt").read(),
            "OVERWRITTEN",
        )

    def test_list_bucket_objects(self):
        self.storage.create_bucket("default-bucket")
        for i in range(100):
            self.storage.save_object(
                "default-bucket", f"file-{i}.txt", b"Hello, world!"
            )
        res = self.storage.list_bucket_objects("default-bucket", page=1, per_page=5)
        self.assertEqual(len(res.items), 5)
        self.assertEqual(res.has_next_page, True)
        self.assertEqual(res.has_previous_page, False)
        self.assertEqual(res.page_number, 1)

        first_item = res.items[0]
        self.assertEqual(first_item.type, "file")
        self.assertEqual(first_item.size, 13)
        self.assertEqual(first_item.content_type, "text/plain")
        res = self.storage.list_bucket_objects("default-bucket", page=2, per_page=100)
        self.assertEqual(len(res.items), 0)
        self.assertEqual(res.has_next_page, False)
        self.assertEqual(res.has_previous_page, True)

    def test_list_bucket_objects_with_query(self):
        self.storage.create_bucket("default-bucket")
        for i in range(100):
            self.storage.save_object(
                "default-bucket", f"file-{i}.txt", b"Hello, world!"
            )
        self.storage.save_object("default-bucket", "found.txt", b"Hello, world!")

        res_found = self.storage.list_bucket_objects(
            "default-bucket", query="found", per_page=100
        )

        self.assertEqual(len(res_found.items), 1)
        self.assertEqual(res_found.items[0].name, "found.txt")

    def test_list_bucket_objects_with_prefix_and_query(self):
        self.storage.create_bucket("default-bucket")
        self.storage.save_object("default-bucket", "prefix/found.txt", b"Hello, world!")
        self.storage.save_object("default-bucket", "tada/found-2.txt", b"Hello, world!")

        self.assertEqual(
            0,
            len(
                self.storage.list_bucket_objects("default-bucket", query="found").items
            ),
        )

        res = self.storage.list_bucket_objects(
            "default-bucket", prefix="prefix", query="found"
        )
        self.assertEqual(len(res.items), 1)
        self.assertEqual(res.items[0].name, "found.txt")

        res = self.storage.list_bucket_objects(
            "default-bucket", prefix="tada", query="found"
        )
        self.assertEqual(len(res.items), 1)
        self.assertEqual(res.items[0].name, "found-2.txt")

    def test_generate_upload_url(self):
        self.storage.create_bucket("default-bucket")
        url = self.storage.generate_upload_url(
            "default-bucket", "file.txt", content_type="text/plain"
        )
        self.assertTrue(url.startswith("http://localhost:8000/files/up/"))
        token = url.split("/")[-2]

        self.assertEqual(
            self.storage._get_payload_from_token(token),
            {"bucket_name": "default-bucket", "file_path": "file.txt"},
        )

    def test_upload_file(self):
        self.storage.create_bucket("default-bucket")

        file_data = BytesIO(b"This is a test file2.")
        uploaded_file = SimpleUploadedFile(
            "test_file.txt", file_data.getvalue(), content_type="text/plain"
        )

        url = self.storage.generate_upload_url(
            "default-bucket", "test_file.txt", "text/plain"
        )
        with patch("hexa.files.views.storage", self.storage):
            resp = self.client.post(
                url,
                data={"file": uploaded_file},
                format="multipart",
                HTTP_X_METHOD_OVERRIDE="PUT",
            )
        self.assertEqual(resp.status_code, 201)

    def test_upload_file_expired_token(self):
        self.storage.create_bucket("default-bucket")

        file_data = BytesIO(b"This is a test file.")
        uploaded_file = SimpleUploadedFile(
            "test_file.txt", file_data.getvalue(), content_type="text/plain"
        )

        # Expire the token
        self.storage._token_max_age = 0

        url = self.storage.generate_upload_url(
            "default-bucket", "test_file.txt", "text/plain"
        )
        with patch("hexa.files.views.storage", self.storage):
            resp = self.client.post(
                url,
                data={"file": uploaded_file},
                format="multipart",
                HTTP_X_METHOD_OVERRIDE="PUT",
            )
        self.assertEqual(resp.status_code, 400)

        # Put back a greater expiration time
        self.storage._token_max_age = 60 * 60
        with patch("hexa.files.views.storage", self.storage):
            resp = self.client.post(
                url,
                data={"file": uploaded_file},
                format="multipart",
                HTTP_X_METHOD_OVERRIDE="PUT",
            )
        self.assertEqual(resp.status_code, 201)

    def test_get_mount_config(self):
        self.assertEqual(
            self.storage.get_bucket_mount_config("my_bucket"),
            {"WORKSPACE_STORAGE_MOUNT_PATH": str(self.data_directory / "my_bucket")},
        )

    def test_delete_bucket(self):
        self.storage.create_bucket("default-bucket")
        self.assertTrue((self.data_directory / "default-bucket").exists())
        self.storage.delete_bucket(
            "default-bucket",
        )
        self.assertFalse(self.storage.exists("default-bucket"))

    def test_delete_bucket_not_empty(self):
        self.storage.create_bucket("default-bucket")
        self.storage.save_object("default-bucket", "file.txt", b"Hello, world!")
        with self.assertRaises(self.storage.exceptions.BadRequest):
            self.storage.delete_bucket("default-bucket")
        self.assertTrue(self.storage.exists("default-bucket"))

        self.storage.delete_bucket("default-bucket", force=True)
        self.assertFalse(self.storage.exists("default-bucket"))
