import shutil
from io import BytesIO
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from django.test import SimpleTestCase

from hexa.core.text_files import MAX_TEXT_FILE_SIZE, TextFiles
from hexa.files.backends.fs import FileSystemStorage
from hexa.files.bucket_file_source import BucketFileSource


class BucketFileSourceTest(SimpleTestCase):
    def setUp(self):
        self.data_directory = Path(mkdtemp())
        self.storage = FileSystemStorage(data_dir=self.data_directory)
        self.storage.create_bucket("bucket")
        for key, content in {
            "readme.md": b"# Hello",
            "data/a.csv": b"x,y",
            "data/nested/b.py": b"print('b')",
            "data/logo.png": b"\x89PNG\x00",
            ".hidden/secret.txt": b"secret",
        }.items():
            self.storage.save_object("bucket", key, BytesIO(content))

    def tearDown(self):
        shutil.rmtree(self.data_directory)

    def test_lists_files_recursively_without_downloading(self):
        with patch.object(self.storage, "read_object") as read_object:
            files = BucketFileSource(self.storage, "bucket")
            self.assertEqual(
                sorted(files),
                ["data/a.csv", "data/logo.png", "data/nested/b.py", "readme.md"],
            )
            read_object.assert_not_called()

    def test_prefix_scopes_the_listing(self):
        files = BucketFileSource(self.storage, "bucket", prefix="data/nested/")
        self.assertEqual(list(files), ["data/nested/b.py"])

    def test_reads_text_once(self):
        files = BucketFileSource(self.storage, "bucket")
        with patch.object(
            self.storage, "read_object", wraps=self.storage.read_object
        ) as read_object:
            self.assertEqual(files["data/a.csv"], "x,y")
            self.assertEqual(files["data/a.csv"], "x,y")
            read_object.assert_called_once_with("bucket", "data/a.csv")

    def test_binary_and_oversized_files_are_none(self):
        self.storage.save_object(
            "bucket", "big.json", BytesIO(b"0" * (MAX_TEXT_FILE_SIZE + 1))
        )
        files = BucketFileSource(self.storage, "bucket")
        self.assertIsNone(files["data/logo.png"])
        self.assertIsNone(files["big.json"])

    def test_unknown_path(self):
        with self.assertRaises(KeyError):
            BucketFileSource(self.storage, "bucket")["nope.txt"]

    def test_listing_stops_at_the_cap(self):
        with patch("hexa.files.bucket_file_source.MAX_LISTED_FILES", 2):
            files = BucketFileSource(self.storage, "bucket")
            self.assertEqual(len(files), 2)
            self.assertTrue(files.truncated)

    def test_grep_through_text_files(self):
        result = TextFiles(BucketFileSource(self.storage, "bucket")).grep(
            "print", glob="**/*.py"
        )
        self.assertEqual(result["files"], ["data/nested/b.py"])
