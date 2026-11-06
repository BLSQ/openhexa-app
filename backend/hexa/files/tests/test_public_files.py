import io
import shutil
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase, override_settings

from hexa.files.backends.dummy import DummyStorageClient
from hexa.files.backends.fs import FileSystemStorage
from hexa.workspaces.tests.testutils import create_workspace


@override_settings(PUBLIC_FILES_ENABLED=True)
class PublicFileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.WORKSPACE = create_workspace(
            name="Public WS",
            slug="public-ws",
            bucket_name="public-ws-bucket",
            public_files_enabled=True,
        )

    def setUp(self):
        self.storage = DummyStorageClient()
        self.storage.create_bucket(self.WORKSPACE.bucket_name)
        for key in ["public/data.csv", "public/maps/tiles.pmtiles", "private.csv"]:
            self.storage.save_object(
                self.WORKSPACE.bucket_name, key, io.BytesIO(b"content")
            )
        self.storage.save_object(
            self.WORKSPACE.bucket_name, "public/.secret", io.BytesIO(b"content")
        )
        self.storage.create_bucket_folder(self.WORKSPACE.bucket_name, "public/maps")
        patcher = patch("hexa.files.views.storage", self.storage)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _url(self, path):
        return f"/files/public/{self.WORKSPACE.slug}/{path}"

    def test_redirects_to_download_url(self):
        for path in ["data.csv", "maps/tiles.pmtiles"]:
            with self.subTest(path=path):
                response = self.client.get(self._url(path))
                self.assertEqual(response.status_code, 302)
                self.assertEqual(
                    response["Location"],
                    f"http://mockstorage.com/{self.WORKSPACE.bucket_name}/public/{path}",
                )
                self.assertEqual(response["Access-Control-Allow-Origin"], "*")
                self.assertEqual(response["Cache-Control"], "public, max-age=300")

    def test_head_is_allowed(self):
        response = self.client.head(self._url("data.csv"))
        self.assertEqual(response.status_code, 302)

    def test_preflight(self):
        response = self.client.options(
            self._url("data.csv"),
            HTTP_ORIGIN="https://example.com",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="range",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        self.assertIn("Range", response["Access-Control-Allow-Headers"])
        self.assertNotIn("Access-Control-Allow-Credentials", response)

    def test_cross_origin_get_keeps_wildcard_origin(self):
        response = self.client.get(
            self._url("data.csv"), HTTP_ORIGIN=settings.NEW_FRONTEND_DOMAIN
        )
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        self.assertNotIn("Access-Control-Allow-Credentials", response)

    def test_post_is_not_allowed(self):
        response = self.client.post(self._url("data.csv"))
        self.assertEqual(response.status_code, 405)

    def test_not_found_paths(self):
        for path in [
            "",
            "maps",
            "maps/",
            "missing.csv",
            ".secret",
            "../private.csv",
            "%2E%2E/private.csv",
            "maps/../../private.csv",
            "~/private.csv",
        ]:
            with self.subTest(path=path):
                response = self.client.get(self._url(path))
                self.assertEqual(response.status_code, 404)

    def test_unknown_workspace(self):
        response = self.client.get("/files/public/unknown-ws/data.csv")
        self.assertEqual(response.status_code, 404)

    def test_workspace_setting_disabled(self):
        self.WORKSPACE.public_files_enabled = False
        self.WORKSPACE.save()
        response = self.client.get(self._url("data.csv"))
        self.assertEqual(response.status_code, 404)

    def test_archived_workspace(self):
        self.WORKSPACE.archived = True
        self.WORKSPACE.save()
        response = self.client.get(self._url("data.csv"))
        self.assertEqual(response.status_code, 404)

    @override_settings(PUBLIC_FILES_ENABLED=False)
    def test_instance_setting_disabled(self):
        response = self.client.get(self._url("data.csv"))
        self.assertEqual(response.status_code, 404)


@override_settings(PUBLIC_FILES_ENABLED=True)
class PublicFileViewFileSystemStorageTest(TestCase):
    """The filesystem backend returns object keys as Path instances, unlike the dummy one."""

    @classmethod
    def setUpTestData(cls):
        cls.WORKSPACE = create_workspace(
            name="Public FS WS",
            slug="public-fs-ws",
            bucket_name="public-fs-ws-bucket",
            public_files_enabled=True,
        )

    def setUp(self):
        data_directory = Path(mkdtemp())
        self.addCleanup(shutil.rmtree, data_directory)
        self.storage = FileSystemStorage(data_dir=data_directory)
        self.storage.create_bucket(self.WORKSPACE.bucket_name)
        self.storage.save_object(
            self.WORKSPACE.bucket_name, "public/data.csv", io.BytesIO(b"a,b\n1,2\n")
        )
        # Both the public view and the download view it redirects to use this storage
        patcher = patch("hexa.files.views.storage", self.storage)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_redirect_can_be_followed_to_the_file(self):
        response = self.client.get(f"/files/public/{self.WORKSPACE.slug}/data.csv")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/files/dl/", response["Location"])

        download = self.client.get(response["Location"].removeprefix(settings.BASE_URL))
        self.assertEqual(download.status_code, 200)
        # Served from the app origin, so it must never be rendered as a page
        self.assertTrue(download["Content-Disposition"].startswith("attachment"))
        self.assertEqual(b"".join(download.streaming_content), b"a,b\n1,2\n")
