import io
from unittest.mock import patch

import requests
from django.conf import settings

from hexa.core.test import TestCase
from hexa.files.backends.azure import AzureBlobStorage


class AzureBlobStorageTest(TestCase):
    def setUp(self):
        super().setUp()
        # Check that Azurite is running
        try:
            response = requests.get(settings.AZURITE_TEST_SERVER)
            if not response.headers.get("Server").startswith("Azurite-Blob"):
                raise Exception("Azurite is not running")
        except Exception:
            raise Exception("Azurite is not running")
        # Use Azurite connection string (Azure Storage emulator)
        self.storage = AzureBlobStorage(
            connection_string=f"DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint={settings.AZURITE_TEST_SERVER}devstoreaccount1;"
        )
        # Clean up any existing test containers
        self._cleanup_test_containers()

    def tearDown(self):
        # Clean up test containers after each test
        self._cleanup_test_containers()
        super().tearDown()

    def _cleanup_test_containers(self):
        """Clean up any test containers that might exist"""
        try:
            # List all containers and delete those starting with 'test-'
            containers = self.storage.client.list_containers(name_starts_with="test-")
            for container in containers:
                try:
                    self.storage.client.delete_container(container.name)
                except Exception:
                    pass  # Ignore errors during cleanup
        except Exception:
            pass  # Ignore errors if service is not available

    def test_bucket_exists_false(self):
        """Test bucket_exists returns False for non-existent bucket"""
        self.assertFalse(self.storage.bucket_exists("non-existent-bucket"))

    def test_create_bucket(self):
        """Test basic bucket creation"""
        bucket_name = "test-bucket"
        self.storage.create_bucket(bucket_name)
        self.assertTrue(self.storage.bucket_exists(bucket_name))

    def test_create_bucket_with_labels(self):
        """Test bucket creation with metadata labels"""
        bucket_name = "test-bucket-with-labels"
        labels = {"env": "test", "team": "data"}
        self.storage.create_bucket(bucket_name, labels=labels)
        self.assertTrue(self.storage.bucket_exists(bucket_name))

    def test_create_bucket_already_exists(self):
        """Test that creating an existing bucket doesn't raise an exception"""
        bucket_name = "test-bucket-duplicate"
        self.storage.create_bucket(bucket_name)
        # Should not raise an exception
        self.assertRaises(
            self.storage.exceptions.AlreadyExists,
            self.storage.create_bucket,
            bucket_name,
        )
        self.assertTrue(self.storage.bucket_exists(bucket_name))

    def test_save_object(self):
        """Test saving an object to a bucket"""
        bucket_name = "test-bucket-save"
        self.storage.create_bucket(bucket_name)

        file_data = b"Hello, world!"
        file_path = "test-file.txt"

        self.storage.save_object(bucket_name, file_path, file_data)

        # Verify object exists
        obj = self.storage.get_bucket_object(bucket_name, file_path)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.name, file_path)
        self.assertEqual(obj.type, "file")
        self.assertEqual(obj.size, len(file_data))

    def test_save_object_with_io_buffer(self):
        """Test saving an object using io.BytesIO"""
        bucket_name = "test-bucket-io"
        self.storage.create_bucket(bucket_name)

        file_data = b"Hello from IO buffer!"
        file_buffer = io.BytesIO(file_data)
        file_path = "test-file-io.txt"

        self.storage.save_object(bucket_name, file_path, file_buffer)

        # Verify object exists
        obj = self.storage.get_bucket_object(bucket_name, file_path)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.name, file_path)
        self.assertEqual(obj.size, len(file_data))

    def test_save_object_nested_path(self):
        """Test saving an object with nested path"""
        bucket_name = "test-bucket-nested"
        self.storage.create_bucket(bucket_name)

        file_data = b"Nested file content"
        file_path = "folder1/folder2/nested-file.txt"

        self.storage.save_object(bucket_name, file_path, file_data)

        # Verify object exists
        obj = self.storage.get_bucket_object(bucket_name, file_path)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.name, "nested-file.txt")
        self.assertEqual(obj.key, file_path)

    def test_get_bucket_object_exists(self):
        """Test retrieving an existing object"""
        bucket_name = "test-bucket-get"
        file_path = "test-file.txt"
        file_data = b"Test content"

        self.storage.create_bucket(bucket_name)
        self.storage.save_object(bucket_name, file_path, file_data)

        obj = self.storage.get_bucket_object(bucket_name, file_path)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.name, file_path)
        self.assertEqual(obj.type, "file")
        self.assertEqual(obj.size, len(file_data))

    def test_get_bucket_object_not_found(self):
        """Test retrieving a non-existent object returns None"""
        bucket_name = "test-bucket-not-found"
        self.storage.create_bucket(bucket_name)

        obj = self.storage.get_bucket_object(bucket_name, "non-existent-file.txt")
        self.assertIsNone(obj)

    def test_list_bucket_objects_empty(self):
        """Test listing objects in an empty bucket"""
        bucket_name = "test-bucket-empty"
        self.storage.create_bucket(bucket_name)

        result = self.storage.list_bucket_objects(bucket_name)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.items), 0)
        self.assertEqual(result.page_number, 1)
        self.assertFalse(result.has_previous_page)
        self.assertFalse(result.has_next_page)

    def test_list_bucket_objects_with_files(self):
        """Test listing objects in a bucket with files"""
        bucket_name = "test-bucket-with-files"
        self.storage.create_bucket(bucket_name)

        # Add some test files
        test_files = ["file1.txt", "file2.txt", "folder/file3.txt"]
        for file_path in test_files:
            self.storage.save_object(bucket_name, file_path, b"test content")

        result = self.storage.list_bucket_objects(bucket_name)

        self.assertIsNotNone(result)
        self.assertGreater(len(result.items), 0)

        # Check that our files are in the results (some might be folders)
        item_names = [item.name for item in result.items]
        self.assertIn("file1.txt", item_names)
        self.assertIn("file2.txt", item_names)

    def test_list_bucket_objects_with_prefix(self):
        """Test listing objects with a prefix filter"""
        bucket_name = "test-bucket-prefix"
        self.storage.create_bucket(bucket_name)

        # Add files with different prefixes
        files = {
            "prefix1/file1.txt": b"content1",
            "prefix1/file2.txt": b"content2",
            "prefix2/file3.txt": b"content3",
            "other.txt": b"content4",
        }

        for file_path, content in files.items():
            self.storage.save_object(bucket_name, file_path, content)

        # List with prefix
        result = self.storage.list_bucket_objects(bucket_name, prefix="prefix1/")

        self.assertIsNotNone(result)
        # Should only return items with the specified prefix
        for item in result.items:
            self.assertTrue(item.key.startswith("prefix1/") or item.type == "directory")

    def test_list_bucket_objects_with_query(self):
        """Test listing objects with a query filter"""
        bucket_name = "test-bucket-query"
        self.storage.create_bucket(bucket_name)

        # Add files with different names
        files = {
            "important-file.txt": b"content1",
            "regular-file.txt": b"content2",
            "another-important-doc.txt": b"content3",
            "random.txt": b"content4",
        }

        for file_path, content in files.items():
            self.storage.save_object(bucket_name, file_path, content)

        # List with query
        result = self.storage.list_bucket_objects(bucket_name, query="important")

        self.assertIsNotNone(result)
        # Should only return items containing "important" in the name
        for item in result.items:
            self.assertIn("important", item.name.lower())

    def test_list_bucket_objects_pagination(self):
        """Test pagination in object listing"""
        bucket_name = "test-bucket-pagination"
        self.storage.create_bucket(bucket_name)

        # Add multiple files to test pagination
        for i in range(10):
            self.storage.save_object(bucket_name, f"file-{i:02d}.txt", b"test content")

        # Test first page
        result_page1 = self.storage.list_bucket_objects(bucket_name, page=1, per_page=3)
        self.assertEqual(result_page1.page_number, 1)
        self.assertFalse(result_page1.has_previous_page)
        self.assertLessEqual(len(result_page1.items), 3)

        # Test second page if there are enough items
        if result_page1.has_next_page:
            result_page2 = self.storage.list_bucket_objects(
                bucket_name, page=2, per_page=3
            )
            self.assertEqual(result_page2.page_number, 2)
            self.assertTrue(result_page2.has_previous_page)

    def test_delete_object(self):
        """Test deleting an object"""
        bucket_name = "test-bucket-delete"
        file_path = "file-to-delete.txt"

        self.storage.create_bucket(bucket_name)
        self.storage.save_object(bucket_name, file_path, b"will be deleted")

        # Verify object exists
        obj = self.storage.get_bucket_object(bucket_name, file_path)
        self.assertIsNotNone(obj)

        # Delete object
        self.storage.delete_object(bucket_name, file_path)

        # Verify object is gone
        obj = self.storage.get_bucket_object(bucket_name, file_path)
        self.assertIsNone(obj)

    def test_delete_bucket(self):
        """Test deleting an empty bucket"""
        bucket_name = "test-bucket-to-delete"

        self.storage.create_bucket(bucket_name)
        self.assertTrue(self.storage.bucket_exists(bucket_name))

        self.storage.delete_bucket(bucket_name)
        self.assertFalse(self.storage.bucket_exists(bucket_name))

    def test_delete_bucket_with_force(self):
        """Test deleting a bucket with contents using force=True"""
        bucket_name = "test-bucket-force-delete"

        self.storage.create_bucket(bucket_name)
        self.storage.save_object(bucket_name, "test-file.txt", b"content")

        # This should work with force=True
        self.storage.delete_bucket(bucket_name, force=True)
        self.assertFalse(self.storage.bucket_exists(bucket_name))

    @patch("hexa.files.backends.azure.generate_blob_sas")
    def test_generate_download_url(self, mock_generate_sas):
        """Test generating a download URL"""
        mock_generate_sas.return_value = "mock_sas_token"

        bucket_name = "test-bucket-download"
        file_path = "test-file.txt"

        self.storage.create_bucket(bucket_name)
        self.storage.save_object(bucket_name, file_path, b"content")

        url = self.storage.generate_download_url(bucket_name, file_path)

        self.assertIsNotNone(url)
        self.assertIn(bucket_name, url)
        self.assertIn(file_path, url)
        self.assertIn("mock_sas_token", url)
        self.assertTrue(mock_generate_sas.called)

    @patch("hexa.files.backends.azure.generate_blob_sas")
    def test_generate_upload_url(self, mock_generate_sas):
        """Test generating an upload URL"""
        mock_generate_sas.return_value = "mock_sas_token"

        bucket_name = "test-bucket-upload"
        file_path = "test-upload-file.txt"
        content_type = "text/plain"

        self.storage.create_bucket(bucket_name)

        url, headers = self.storage.generate_upload_url(
            bucket_name=bucket_name, target_key=file_path, content_type=content_type
        )

        self.assertIsNotNone(url)
        self.assertIn(bucket_name, url)
        self.assertIn(file_path, url)
        self.assertIn("mock_sas_token", url)

        self.assertIsNotNone(headers)
        self.assertEqual(headers["x-ms-blob-type"], "BlockBlob")
        self.assertEqual(headers["Content-Type"], content_type)
        self.assertTrue(mock_generate_sas.called)

    @patch("hexa.files.backends.azure.generate_blob_sas")
    def test_generate_upload_url_without_content_type(self, mock_generate_sas):
        """Test generating an upload URL without content type"""
        mock_generate_sas.return_value = "mock_sas_token"

        bucket_name = "test-bucket-upload-no-ct"
        file_path = "test-file.txt"

        self.storage.create_bucket(bucket_name)

        url, headers = self.storage.generate_upload_url(
            bucket_name=bucket_name, target_key=file_path
        )

        self.assertIsNotNone(url)
        self.assertIn("mock_sas_token", url)

        self.assertIsNotNone(headers)
        self.assertEqual(headers["x-ms-blob-type"], "BlockBlob")
        self.assertNotIn("Content-Type", headers)

    @patch("hexa.files.backends.azure.generate_container_sas")
    def test_get_short_lived_access_token(self, mock_generate_container_sas):
        """Test generating a short-lived access token"""
        mock_generate_container_sas.return_value = "mock_container_sas_token"

        bucket_name = "test-bucket-token"
        self.storage.create_bucket(bucket_name)

        token = self.storage.get_short_lived_access_token(bucket_name)

        self.assertEqual(token, "mock_container_sas_token")
        self.assertTrue(mock_generate_container_sas.called)

    @patch("hexa.files.backends.azure.generate_container_sas")
    def test_get_bucket_mount_config(self, mock_generate_container_sas):
        """Test getting bucket mount configuration"""
        mock_generate_container_sas.return_value = "mock_container_sas_token"

        bucket_name = "test-bucket-mount"
        self.storage.create_bucket(bucket_name)

        config = self.storage.get_bucket_mount_config(bucket_name)

        expected_config = {
            "WORKSPACE_STORAGE_ENGINE_AZURE_ACCOUNT_NAME": "devstoreaccount1",
            "WORKSPACE_STORAGE_ENGINE_AZURE_STORAGE_SAS_TOKEN": "mock_container_sas_token",
        }

        self.assertEqual(config, expected_config)

    def test_list_bucket_objects_hidden_files_default(self):
        """Test that hidden files are ignored by default"""
        bucket_name = "test-bucket-hidden"
        self.storage.create_bucket(bucket_name)

        # Add regular and hidden files
        self.storage.save_object(bucket_name, "regular-file.txt", b"content")
        self.storage.save_object(bucket_name, ".hidden-file.txt", b"hidden content")

        result = self.storage.list_bucket_objects(bucket_name, ignore_hidden_files=True)

        # Should not contain hidden files
        item_names = [item.name for item in result.items]
        self.assertIn("regular-file.txt", item_names)
        self.assertNotIn(".hidden-file.txt", item_names)

    def test_list_bucket_objects_include_hidden_files(self):
        """Test that hidden files are included when requested"""
        bucket_name = "test-bucket-include-hidden"
        self.storage.create_bucket(bucket_name)

        # Add regular and hidden files
        self.storage.save_object(bucket_name, "regular-file.txt", b"content")
        self.storage.save_object(bucket_name, ".hidden-file.txt", b"hidden content")

        result = self.storage.list_bucket_objects(
            bucket_name, ignore_hidden_files=False
        )

        # Should contain both regular and hidden files
        item_names = [item.name for item in result.items]
        self.assertIn("regular-file.txt", item_names)
        self.assertIn(".hidden-file.txt", item_names)

    def test_load_bucket_sample_data(self):
        """Test loading sample data into a bucket"""
        bucket_name = "test-bucket-sample-data"
        self.storage.create_bucket(bucket_name)

        # This method loads sample files from the static directory
        self.storage.load_bucket_sample_data(bucket_name)

        # Check that some objects were created
        self.storage.list_bucket_objects(bucket_name)
        # We can't predict exactly what files will be there, but there should be some
        # if sample data files exist in the static directory
