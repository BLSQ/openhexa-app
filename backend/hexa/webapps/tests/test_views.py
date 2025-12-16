import io
import zipfile

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

    def test_serve_bundle_webapp(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("index.html", "<html><body>Bundle Test</body></html>")
            zip_file.writestr("static/js/app.js", "console.log('test');")

        bundle_webapp = Webapp.objects.create(
            name="Bundle Test",
            slug="bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle=zip_buffer.getvalue(),
            workspace=self.workspace,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bundle Test", response.content)

    def test_serve_bundle_webapp_static_file(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("index.html", "<html><body>Test</body></html>")
            zip_file.writestr("static/js/app.js", "console.log('test');")

        bundle_webapp = Webapp.objects.create(
            name="Bundle Test",
            slug="bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle=zip_buffer.getvalue(),
            workspace=self.workspace,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/static/js/app.js"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"console.log", response.content)

    def test_serve_bundle_webapp_path_traversal_blocked(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("index.html", "<html><body>Test</body></html>")

        bundle_webapp = Webapp.objects.create(
            name="Bundle Test",
            slug="bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle=zip_buffer.getvalue(),
            workspace=self.workspace,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/../../../etc/passwd"
        )

        self.assertEqual(response.status_code, 404)

    def test_serve_bundle_webapp_hidden_files_blocked(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("index.html", "<html><body>Test</body></html>")
            zip_file.writestr(".env", "SECRET_KEY=sensitive_data")
            zip_file.writestr(".git/config", "[core]")

        bundle_webapp = Webapp.objects.create(
            name="Bundle Test",
            slug="bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle=zip_buffer.getvalue(),
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

    def test_serve_bundle_webapp_nested_structure(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "build/index.html", "<html><body>Build Test</body></html>"
            )
            zip_file.writestr("build/static/main.js", "console.log('main');")

        bundle_webapp = Webapp.objects.create(
            name="Nested Bundle Test",
            slug="nested-bundle-test",
            type=Webapp.WebappType.BUNDLE,
            bundle=zip_buffer.getvalue(),
            workspace=self.workspace,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{bundle_webapp.slug}/bundle/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Build Test", response.content)

    def test_change_webapp_type_iframe_to_bundle(self):
        iframe_webapp = Webapp.objects.create(
            name="iFrame Test",
            slug="iframe-test",
            type=Webapp.WebappType.IFRAME,
            url="https://example.com",
            workspace=self.workspace,
            created_by=self.user,
        )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "index.html", "<html><body>Changed to Bundle</body></html>"
            )

        iframe_webapp.type = Webapp.WebappType.BUNDLE
        iframe_webapp.url = ""
        iframe_webapp.bundle = zip_buffer.getvalue()
        iframe_webapp.save()

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{iframe_webapp.slug}/bundle/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Changed to Bundle", response.content)

    def test_change_webapp_type_html_to_bundle(self):
        html_webapp = Webapp.objects.create(
            name="HTML Test",
            slug="html-test",
            type=Webapp.WebappType.HTML,
            content="<html><body>Old HTML</body></html>",
            workspace=self.workspace,
            created_by=self.user,
        )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "index.html", "<html><body>Changed to Bundle</body></html>"
            )

        html_webapp.type = Webapp.WebappType.BUNDLE
        html_webapp.content = ""
        html_webapp.bundle = zip_buffer.getvalue()
        html_webapp.save()

        self.client.force_login(self.user)
        response = self.client.get(
            f"/webapps/{self.workspace.slug}/{html_webapp.slug}/bundle/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Changed to Bundle", response.content)
