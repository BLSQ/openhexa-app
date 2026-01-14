import io
import zipfile
from unittest.mock import Mock, patch

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.webapps.schema.mutations import _upload_bundle_to_storage
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class BundleStorageTest(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.user = User.objects.create_user("test@bluesquarehub.com", "password")
        WorkspaceMembership.objects.create(
            user=self.user,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def _create_test_bundle(self, files):
        bundle_io = io.BytesIO()
        with zipfile.ZipFile(bundle_io, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path, content in files.items():
                zip_file.writestr(file_path, content)
        return bundle_io.getvalue()

    @patch("hexa.files.storage")
    def test_upload_bundle_to_storage_success(self, mock_storage):
        mock_storage.list_bucket_objects.side_effect = mock_storage.exceptions.NotFound
        mock_storage.save_object = Mock()

        files = {
            "index.html": "<html><body>Test</body></html>",
            "static/js/app.js": "console.log('test');",
            "static/css/main.css": "body { margin: 0; }",
        }
        bundle_bytes = self._create_test_bundle(files)

        manifest = _upload_bundle_to_storage(
            self.workspace, "test-webapp", bundle_bytes
        )

        self.assertEqual(len(manifest), 3)
        self.assertEqual(manifest[0]["path"], "index.html")
        self.assertEqual(manifest[1]["path"], "static/js/app.js")
        self.assertEqual(manifest[2]["path"], "static/css/main.css")

        self.assertEqual(mock_storage.save_object.call_count, 3)

    @patch("hexa.files.storage")
    def test_upload_bundle_filters_hidden_files(self, mock_storage):
        mock_storage.list_bucket_objects.side_effect = mock_storage.exceptions.NotFound
        mock_storage.save_object = Mock()

        files = {
            "index.html": "<html><body>Test</body></html>",
            ".env": "SECRET=value",
            ".git/config": "[core]",
            "static/.hidden": "hidden content",
        }
        bundle_bytes = self._create_test_bundle(files)

        manifest = _upload_bundle_to_storage(
            self.workspace, "test-webapp", bundle_bytes
        )

        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["path"], "index.html")

        self.assertEqual(mock_storage.save_object.call_count, 1)

    @patch("hexa.files.storage")
    def test_upload_bundle_replaces_existing(self, mock_storage):
        mock_obj1 = Mock()
        mock_obj1.key = "webapps/test-webapp/old-file.html"
        mock_obj2 = Mock()
        mock_obj2.key = "webapps/test-webapp/old-script.js"

        mock_page = Mock()
        mock_page.items = [mock_obj1, mock_obj2]
        mock_storage.list_bucket_objects.return_value = mock_page
        mock_storage.delete_object = Mock()
        mock_storage.save_object = Mock()

        files = {"index.html": "<html><body>New</body></html>"}
        bundle_bytes = self._create_test_bundle(files)

        manifest = _upload_bundle_to_storage(
            self.workspace, "test-webapp", bundle_bytes
        )

        self.assertEqual(mock_storage.delete_object.call_count, 2)
        mock_storage.delete_object.assert_any_call(
            self.workspace.bucket_name, "webapps/test-webapp/old-file.html"
        )
        mock_storage.delete_object.assert_any_call(
            self.workspace.bucket_name, "webapps/test-webapp/old-script.js"
        )

        self.assertEqual(len(manifest), 1)

    @patch("hexa.files.storage")
    def test_upload_bundle_creates_manifest(self, mock_storage):
        mock_storage.list_bucket_objects.side_effect = mock_storage.exceptions.NotFound
        mock_storage.save_object = Mock()

        files = {
            "index.html": "<html></html>",
            "app.js": "console.log('test');",
        }
        bundle_bytes = self._create_test_bundle(files)

        manifest = _upload_bundle_to_storage(
            self.workspace, "test-webapp", bundle_bytes
        )

        self.assertEqual(len(manifest), 2)
        self.assertIn("path", manifest[0])
        self.assertIn("size", manifest[0])
        self.assertEqual(manifest[0]["size"], len(files["index.html"]))
        self.assertEqual(manifest[1]["size"], len(files["app.js"]))
