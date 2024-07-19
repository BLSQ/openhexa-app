import os
import shutil
from pathlib import Path
from tempfile import mkdtemp

from hexa.core.test import TestCase
from hexa.files.backends.fs import FileSystemStorage


class FileSystemStorageTest(TestCase):
    storage = None

    def setUp(self):
        super().setUp()
        self.data_directory = Path(mkdtemp())
        self.storage = FileSystemStorage(location=self.data_directory)

    def tearDown(self) -> None:
        super().tearDown()
        shutil.rmtree(self.data_directory)

    def test_create_bucket(self):
        self.storage.create_bucket("test")
        self.assertTrue(self.storage.exists("test"))
        self.assertTrue(os.path.lexists(self.storage.path("test")))
        self.assertEqual(
            self.storage.path("test"), os.path.join(self.data_directory, "test")
        )

    def test_suspicious_create_bucket(self):
        for path in ["../test", "/test", "../../test", "dir/subdir"]:
            with self.assertRaises(self.storage.exceptions.SuspiciousFileOperation):
                self.storage.create_bucket(path)

    def test_path(self):
        self.assertEqual(
            self.storage.path("my-dir/my-subdir/my-file.png"),
            os.path.join(self.data_directory, "my-dir/my-subdir/my-file.png"),
        )
        self.assertEqual(
            self.storage.path("my-dir/../my-dir/my-subdir/my-file.png"),
            os.path.join(self.data_directory, "my-dir/my-subdir/my-file.png"),
        )

        with self.assertRaises(self.storage.exceptions.SuspiciousFileOperation):
            self.storage.path("../my-dir/my-subdir/my-file.png")

    def test_bucket_path(self):
        self.assertEqual(
            self.storage.bucket_path("my-bucket", "my-dir/my-subdir/my-file.png"),
            os.path.join(self.data_directory, "my-bucket/my-dir/my-subdir/my-file.png"),
        )
        self.assertEqual(
            self.storage.bucket_path(
                "my-bucket", "my-dir/../my-dir/my-subdir/my-file.png"
            ),
            os.path.join(self.data_directory, "my-bucket/my-dir/my-subdir/my-file.png"),
        )

        with self.assertRaises(self.storage.exceptions.SuspiciousFileOperation):
            self.storage.bucket_path("my-bucket", "../my-dir/my-subdir/my-file.png")

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
        dir = self.storage.create_bucket_folder("default-bucket", "éà_?_d 1")
        self.assertEqual(dir, "éà__d_1")

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
        res = self.storage.list_bucket_objects("default-bucket", page=1, per_page=30)
        print(res)
