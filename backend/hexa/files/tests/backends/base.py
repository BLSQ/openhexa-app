import io

from hexa.files.backends.base import Storage

BUCKET = "test-bucket"


class StorageTestMixin:
    """
    Contract tests for any Storage backend. Inherit alongside TestCase and
    assign self.storage in setUp.

    TestCase is not inherited here directly as otherwise Django's test runner
    would find it, treat it as a concrete test class, and try to run all its tests,
    which is not wanted here (it would fail instantly)
    """

    storage: Storage

    # --- Bucket ---

    def test_bucket_exists_false(self):
        self.assertFalse(self.storage.bucket_exists(BUCKET))

    def test_create_bucket(self):
        self.storage.create_bucket(BUCKET)
        self.assertTrue(self.storage.bucket_exists(BUCKET))

    def test_create_bucket_already_exists(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(self.storage.exceptions.AlreadyExists):
            self.storage.create_bucket(BUCKET)

    def test_delete_bucket_not_found(self):
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.delete_bucket(BUCKET)

    # --- Object CRUD ---

    def test_save_and_read_object(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"hello world"))
        self.assertEqual(self.storage.read_object(BUCKET, "file.txt"), b"hello world")

    def test_read_object_not_found(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.read_object(BUCKET, "nonexistent.txt")

    def test_overwrite_object(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"original"))
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"overwritten"))
        self.assertEqual(self.storage.read_object(BUCKET, "file.txt"), b"overwritten")

    def test_get_bucket_object_file(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"content"))
        obj = self.storage.get_bucket_object(BUCKET, "file.txt")
        self.assertEqual(obj.name, "file.txt")
        self.assertEqual(obj.type, "file")
        self.assertEqual(obj.size, 7)

    def test_get_bucket_object_not_found(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.get_bucket_object(BUCKET, "nonexistent.txt")

    # --- Folders ---

    def test_create_bucket_folder(self):
        self.storage.create_bucket(BUCKET)
        obj = self.storage.create_bucket_folder(BUCKET, "my-dir")
        self.assertEqual(obj.type, "directory")
        self.assertEqual(obj.name, "my-dir")

    def test_create_bucket_folder_with_trailing_slash(self):
        self.storage.create_bucket(BUCKET)
        obj = self.storage.create_bucket_folder(BUCKET, "my-dir/")
        self.assertEqual(obj.type, "directory")
        self.assertEqual(obj.name, "my-dir")

    # --- List ---

    def test_list_bucket_objects(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file1.txt", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "file2.txt", io.BytesIO(b"b"))
        items = self.storage.list_bucket_objects(BUCKET).items
        self.assertEqual(len(items), 2)
        names = {o.name for o in items}
        self.assertIn("file1.txt", names)
        self.assertIn("file2.txt", names)

    def test_list_bucket_objects_empty(self):
        self.storage.create_bucket(BUCKET)
        result = self.storage.list_bucket_objects(BUCKET)
        self.assertEqual(len(result.items), 0)
        self.assertEqual(result.page_number, 1)
        self.assertFalse(result.has_previous_page)
        self.assertFalse(result.has_next_page)

    def test_list_bucket_objects_with_prefix(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "dir/file1.txt", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "other/file2.txt", io.BytesIO(b"b"))
        items = self.storage.list_bucket_objects(BUCKET, prefix="dir/").items
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "file1.txt")

    def test_list_bucket_objects_nested_not_at_root(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "dir/nested.txt", io.BytesIO(b"a"))
        self.storage.save_object(BUCKET, "root.txt", io.BytesIO(b"b"))
        items = self.storage.list_bucket_objects(BUCKET).items
        names = {o.name for o in items}
        self.assertIn("root.txt", names)
        self.assertNotIn("nested.txt", names)

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

    # --- Delete ---

    def test_delete_object(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"a"))
        self.storage.delete_object(BUCKET, "file.txt")
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.get_bucket_object(BUCKET, "file.txt")

    def test_delete_object_not_found(self):
        self.storage.create_bucket(BUCKET)
        with self.assertRaises(self.storage.exceptions.NotFound):
            self.storage.delete_object(BUCKET, "nonexistent.txt")

    # --- URL generation ---

    def test_generate_download_url(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "file.txt", io.BytesIO(b"a"))
        url = self.storage.generate_download_url(
            bucket_name=BUCKET, target_key="file.txt"
        )
        self.assertIsNotNone(url)

    def test_generate_upload_url(self):
        self.storage.create_bucket(BUCKET)
        url, _ = self.storage.generate_upload_url(
            bucket_name=BUCKET, target_key="new.txt"
        )
        self.assertIsNotNone(url)

    def test_generate_upload_url_raise_if_exists(self):
        self.storage.create_bucket(BUCKET)
        self.storage.save_object(BUCKET, "existing.txt", io.BytesIO(b"a"))
        with self.assertRaises(self.storage.exceptions.AlreadyExists):
            self.storage.generate_upload_url(
                bucket_name=BUCKET,
                target_key="existing.txt",
                raise_if_exists=True,
            )

    # --- Sample data ---

    def test_load_bucket_sample_data(self):
        self.storage.create_bucket(BUCKET)
        self.storage.load_bucket_sample_data(BUCKET)
        items = self.storage.list_bucket_objects(
            BUCKET, ignore_hidden_files=False
        ).items
        self.assertGreater(len(items), 0)
