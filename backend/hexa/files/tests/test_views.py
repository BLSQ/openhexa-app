import shutil
from io import BytesIO
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from django.urls import reverse

from hexa.core.test import TestCase
from hexa.files import storage
from hexa.files.backends.fs import FileSystemStorage
from hexa.files.views import PUBLIC_FILE_REDIRECT_MAX_AGE
from hexa.user_management.models import User
from hexa.workspaces.tests.testutils import create_workspace


class PublicFileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "admin@bluesquarehub.com", "password", is_superuser=True
        )
        cls.WORKSPACE = create_workspace(cls.USER, name="Public files")
        cls.WORKSPACE.public_files_enabled = True
        cls.WORKSPACE.save()
        cls.PRIVATE_WORKSPACE = create_workspace(cls.USER, name="Private files")
        for workspace in (cls.WORKSPACE, cls.PRIVATE_WORKSPACE):
            bucket = workspace.bucket_name
            storage.save_object(bucket, "public/data.json", BytesIO(b"{}"))
            storage.save_object(bucket, "public/tiles/map.pmtiles", BytesIO(b"PM"))
            storage.save_object(bucket, "secret.csv", BytesIO(b"a,b"))
            storage.buckets[bucket]["public/tiles"] = {}

    def url(self, path, workspace=None):
        workspace = workspace or self.WORKSPACE
        return reverse(
            "files:public_file",
            kwargs={"workspace_slug": workspace.slug, "path": path},
        )

    def test_redirects_anonymous_visitor_to_download_url(self):
        response = self.client.get(self.url("public/data.json"))

        self.assertEqual(302, response.status_code)
        self.assertEqual(
            f"http://mockstorage.com/{self.WORKSPACE.bucket_name}/public/data.json",
            response["Location"],
        )
        self.assertEqual(
            f"public, max-age={PUBLIC_FILE_REDIRECT_MAX_AGE}",
            response["Cache-Control"],
        )

    def test_nested_file(self):
        response = self.client.get(self.url("public/tiles/map.pmtiles"))
        self.assertEqual(302, response.status_code)

    def test_head(self):
        response = self.client.head(self.url("public/data.json"))
        self.assertEqual(302, response.status_code)

    def test_not_found_outside_public_folder(self):
        for path in [
            "secret.csv",
            "public",
            "public/",
            "public/../secret.csv",
            "public/tiles",
            "public/missing.json",
            "",
            "../public/data.json",
        ]:
            with self.subTest(path=path):
                response = self.client.get(self.url(path))
                self.assertEqual(404, response.status_code)

    def test_not_found_when_workspace_has_not_enabled_public_files(self):
        response = self.client.get(
            self.url("public/data.json", workspace=self.PRIVATE_WORKSPACE)
        )
        self.assertEqual(404, response.status_code)

    def test_not_found_when_workspace_is_archived(self):
        self.WORKSPACE.archived = True
        self.WORKSPACE.save()

        response = self.client.get(self.url("public/data.json"))
        self.assertEqual(404, response.status_code)

    def test_not_found_for_unknown_workspace(self):
        response = self.client.get("/files/public/nope/public/data.json")
        self.assertEqual(404, response.status_code)

    def test_any_origin_is_allowed(self):
        origin = "https://dashboard.example.org"
        response = self.client.get(self.url("public/data.json"), HTTP_ORIGIN=origin)

        self.assertEqual(302, response.status_code)
        self.assertEqual(origin, response["Access-Control-Allow-Origin"])

    def test_preflight_allows_range_requests(self):
        origin = "https://dashboard.example.org"
        response = self.client.options(
            self.url("public/tiles/map.pmtiles"),
            HTTP_ORIGIN=origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="range",
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(origin, response["Access-Control-Allow-Origin"])
        self.assertIn("range", response["Access-Control-Allow-Headers"].split(", "))
        self.assertIn(
            "content-range", response["Access-Control-Expose-Headers"].split(", ")
        )


class DownloadFileViewTest(TestCase):
    """The filesystem backend serves files itself, so it is the one backend where
    byte ranges are OpenHEXA's job rather than the bucket's.
    """

    def setUp(self):
        super().setUp()
        self.data_directory = Path(mkdtemp())
        self.storage = FileSystemStorage(data_dir=self.data_directory)
        self.storage.create_bucket("bucket")
        self.storage.save_object("bucket", "public/data.bin", BytesIO(b"0123456789"))
        self.storage.create_bucket_folder("bucket", "public/folder")
        patcher = patch("hexa.files.views.storage", self.storage)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_directory)

    def download_url(self, key):
        url = self.storage.generate_download_url(bucket_name="bucket", target_key=key)
        return url[url.index("/files/dl/") :]

    def test_full_file(self):
        response = self.client.get(self.download_url("public/data.bin"))

        self.assertEqual(200, response.status_code)
        self.assertEqual(b"0123456789", b"".join(response.streaming_content))
        self.assertEqual("10", response["Content-Length"])
        self.assertEqual("bytes", response["Accept-Ranges"])
        self.assertEqual("application/octet-stream", response["Content-Type"])

    def test_range(self):
        response = self.client.get(
            self.download_url("public/data.bin"), HTTP_RANGE="bytes=2-4"
        )

        self.assertEqual(206, response.status_code)
        self.assertEqual(b"234", b"".join(response.streaming_content))
        self.assertEqual("3", response["Content-Length"])
        self.assertEqual("bytes 2-4/10", response["Content-Range"])
        self.assertEqual("bytes", response["Accept-Ranges"])

    def test_open_ended_range_is_clamped(self):
        response = self.client.get(
            self.download_url("public/data.bin"), HTTP_RANGE="bytes=7-"
        )

        self.assertEqual(206, response.status_code)
        self.assertEqual(b"789", b"".join(response.streaming_content))
        self.assertEqual("bytes 7-9/10", response["Content-Range"])

        response = self.client.get(
            self.download_url("public/data.bin"), HTTP_RANGE="bytes=7-100"
        )
        self.assertEqual(206, response.status_code)
        self.assertEqual(b"789", b"".join(response.streaming_content))

    def test_suffix_range(self):
        response = self.client.get(
            self.download_url("public/data.bin"), HTTP_RANGE="bytes=-3"
        )

        self.assertEqual(206, response.status_code)
        self.assertEqual(b"789", b"".join(response.streaming_content))
        self.assertEqual("bytes 7-9/10", response["Content-Range"])

    def test_unsatisfiable_range(self):
        for header in ["bytes=10-", "bytes=5-2", "bytes=-0", "bytes=-", "items=1-2"]:
            with self.subTest(header=header):
                response = self.client.get(
                    self.download_url("public/data.bin"), HTTP_RANGE=header
                )
                self.assertEqual(416, response.status_code)
                self.assertEqual("bytes */10", response["Content-Range"])

    def test_any_origin_is_allowed(self):
        origin = "https://dashboard.example.org"
        response = self.client.get(
            self.download_url("public/data.bin"), HTTP_ORIGIN=origin
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(origin, response["Access-Control-Allow-Origin"])

    def test_directory_is_not_found(self):
        response = self.client.get(self.download_url("public/folder"))
        self.assertEqual(404, response.status_code)

    def test_invalid_token(self):
        response = self.client.get("/files/dl/not-a-token/")
        self.assertEqual(400, response.status_code)
