from unittest.mock import Mock, patch

from django.test import Client

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
    create_workspace_slug,
    generate_database_name,
    make_random_password,
)


class WebappViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.workspace = Workspace.objects.create(
            name="Test Workspace",
            slug=create_workspace_slug("Test Workspace"),
            db_name=generate_database_name(),
            db_password=make_random_password(length=16),
        )
        self.user = User.objects.create_user(
            "test@bluesquarehub.com",
            "testpassword",
        )
        WorkspaceMembership.objects.create(
            user=self.user,
            workspace=self.workspace,
            role=WorkspaceMembershipRole.ADMIN,
        )

    def test_serve_html_webapp(self):
        html_webapp = Webapp.objects.create(
            name="HTML Test",
            slug="html-test",
            type=Webapp.WebappType.HTML,
            content="<html><body><h1>Test Content</h1></body></html>",
            workspace=self.workspace,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{html_webapp.slug}/html/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertIn(b"Test Content", response.content)

    def test_serve_html_webapp_unauthorized(self):
        html_webapp = Webapp.objects.create(
            name="HTML Test",
            slug="html-test",
            type=Webapp.WebappType.HTML,
            content="<html><body><h1>Test Content</h1></body></html>",
            workspace=self.workspace,
            created_by=self.user,
        )

        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{html_webapp.slug}/html/"
        )

        self.assertIn(response.status_code, [302, 404])

    def test_serve_html_webapp_wrong_type(self):
        iframe_webapp = Webapp.objects.create(
            name="iFrame Test",
            slug="iframe-test",
            type=Webapp.WebappType.IFRAME,
            url="https://example.com",
            workspace=self.workspace,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{iframe_webapp.slug}/html/"
        )

        self.assertEqual(response.status_code, 404)

    @patch("hexa.webapps.views._read_file_from_storage")
    @patch("hexa.files.storage")
    def test_serve_bundle_webapp(self, mock_storage, mock_read_file):
        bundle_webapp = Webapp.objects.create(
            name="Bundle Test",
            slug="bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle_manifest=[
                {"path": "index.html", "size": 39},
                {"path": "static/js/app.js", "size": 21},
            ],
            workspace=self.workspace,
            created_by=self.user,
        )

        mock_storage.get_bucket_object.return_value = Mock()
        mock_read_file.return_value = b"<html><body>Bundle Test</body></html>"

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bundle Test", response.content)
        mock_storage.get_bucket_object.assert_called_once_with(
            self.workspace.bucket_name, f"webapps/{bundle_webapp.slug}/index.html"
        )

    @patch("hexa.webapps.views._read_file_from_storage")
    @patch("hexa.files.storage")
    def test_serve_bundle_webapp_static_file(self, mock_storage, mock_read_file):
        bundle_webapp = Webapp.objects.create(
            name="Bundle Test",
            slug="bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle_manifest=[
                {"path": "index.html", "size": 32},
                {"path": "static/js/app.js", "size": 21},
            ],
            workspace=self.workspace,
            created_by=self.user,
        )

        mock_storage.get_bucket_object.return_value = Mock()
        mock_read_file.return_value = b"console.log('test');"

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/static/js/app.js"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"console.log", response.content)
        mock_storage.get_bucket_object.assert_called_once_with(
            self.workspace.bucket_name, f"webapps/{bundle_webapp.slug}/static/js/app.js"
        )

    def test_serve_bundle_webapp_path_traversal_blocked(self):
        bundle_webapp = Webapp.objects.create(
            name="Bundle Test",
            slug="bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle_manifest=[{"path": "index.html", "size": 32}],
            workspace=self.workspace,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/../../../etc/passwd"
        )

        self.assertEqual(response.status_code, 404)

    def test_serve_bundle_webapp_hidden_files_blocked(self):
        bundle_webapp = Webapp.objects.create(
            name="Bundle Test",
            slug="bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle_manifest=[{"path": "index.html", "size": 32}],
            workspace=self.workspace,
            created_by=self.user,
        )

        self.client.force_login(self.user)

        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/.env"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/.git/config"
        )
        self.assertEqual(response.status_code, 404)

    @patch("hexa.webapps.views._read_file_from_storage")
    @patch("hexa.files.storage")
    def test_serve_bundle_webapp_nested_structure(self, mock_storage, mock_read_file):
        bundle_webapp = Webapp.objects.create(
            name="Nested Bundle Test",
            slug="nested-bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle_manifest=[
                {"path": "build/index.html", "size": 40},
                {"path": "build/static/main.js", "size": 22},
            ],
            workspace=self.workspace,
            created_by=self.user,
        )

        mock_storage.get_bucket_object.return_value = Mock()
        mock_read_file.return_value = b"<html><body>Build Test</body></html>"

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Build Test", response.content)
        mock_storage.get_bucket_object.assert_called_once_with(
            self.workspace.bucket_name, f"webapps/{bundle_webapp.slug}/build/index.html"
        )
