import tempfile
from unittest.mock import MagicMock, patch

import httpx
from django.test import SimpleTestCase

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.files import (
    MAX_UPLOAD_SIZE,
    FilesCopier,
    download,
    is_skipped,
    upload,
    walk,
)
from hexa.workspace_copier.results import CopyResult
from hexa.workspace_copier.transport import GraphQLError


def fake_download(contents: dict[str, bytes | Exception]):
    """Stub for `download`, which writes into the caller's buffer.

    A mapping rather than a side_effect list so tests that skip some files
    don't depend on how many times it is called.
    """

    def _download(client, slug, path, http_client, destination):
        payload = contents[path]
        if isinstance(payload, Exception):
            raise payload
        return destination.write(payload)

    return _download


def fake_walk(source_objects, target_objects=()):
    """Stub for `walk`: the copier lists the target first, then walks the source."""
    return [iter(target_objects), iter(source_objects)]


class FilesCopierRemoteTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.result = CopyResult()

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_copies_each_file(self, mock_walk, mock_download, mock_upload):
        mock_walk.side_effect = fake_walk(
            [{"key": "a.txt", "size": 3}, {"key": "dir/b.txt", "size": 5}]
        )
        mock_download.side_effect = fake_download(
            {"a.txt": b"abc", "dir/b.txt": b"hello"}
        )

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.copied, [("a.txt", 3), ("dir/b.txt", 5)])
        self.assertEqual(mock_upload.call_count, 2)

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_upload_gets_the_downloaded_bytes_from_the_start_of_the_spool(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.side_effect = fake_walk([{"key": "a.txt", "size": 5}])
        mock_download.side_effect = fake_download({"a.txt": b"hello"})
        uploaded = []
        mock_upload.side_effect = lambda client, slug, path, buf, http: uploaded.append(
            buf.read()
        )

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(uploaded, [b"hello"])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_file_above_single_part_limit_is_failed_without_transferring(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.side_effect = fake_walk(
            [
                {"key": "huge.json", "size": MAX_UPLOAD_SIZE + 1},
                {"key": "ok", "size": 2},
            ]
        )
        mock_download.side_effect = fake_download({"ok": b"ok"})

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(len(self.result.files.failed), 1)
        path, reason = self.result.files.failed[0]
        self.assertEqual(path, "huge.json")
        self.assertIn("TooLarge", reason)
        self.assertEqual(self.result.files.copied, [("ok", 2)])
        self.assertEqual(mock_upload.call_count, 1)

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_failed_file_is_recorded_and_loop_continues(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.side_effect = fake_walk(
            [{"key": "bad.txt", "size": 1}, {"key": "ok.txt", "size": 2}]
        )
        mock_download.side_effect = fake_download(
            {"bad.txt": GraphQLError("boom"), "ok.txt": b"ok"}
        )

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.failed, [("bad.txt", "GraphQLError: boom")])
        self.assertEqual(self.result.files.copied, [("ok.txt", 2)])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_httpx_error_during_transfer_is_recorded_and_loop_continues(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.side_effect = fake_walk(
            [{"key": "bad.txt", "size": 1}, {"key": "ok.txt", "size": 2}]
        )
        mock_download.side_effect = fake_download(
            {"bad.txt": httpx.ReadTimeout("blip"), "ok.txt": b"ok"}
        )

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.failed, [("bad.txt", "ReadTimeout: blip")])
        self.assertEqual(self.result.files.copied, [("ok.txt", 2)])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_spool_write_failure_is_recorded_and_loop_continues(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.side_effect = fake_walk(
            [{"key": "bad.txt", "size": 1}, {"key": "ok.txt", "size": 2}]
        )
        mock_download.side_effect = fake_download(
            {"bad.txt": OSError("No space left on device"), "ok.txt": b"ok"}
        )

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(
            self.result.files.failed, [("bad.txt", "OSError: No space left on device")]
        )
        self.assertEqual(self.result.files.copied, [("ok.txt", 2)])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_skips_target_files_matching_key_and_size(
        self, mock_walk, mock_download, mock_upload
    ):
        # 'same.txt' matches key+size and is skipped; 'grew.txt' exists but
        # with a different size so it is re-copied; 'new.txt' is absent.
        mock_walk.side_effect = fake_walk(
            [
                {"key": "same.txt", "size": 3},
                {"key": "grew.txt", "size": 5},
                {"key": "new.txt", "size": 2},
            ],
            [{"key": "same.txt", "size": 3}, {"key": "grew.txt", "size": 1}],
        )
        mock_download.side_effect = fake_download(
            {"grew.txt": b"12345", "new.txt": b"12"}
        )

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(
            set(self.result.files.copied), {("grew.txt", 5), ("new.txt", 2)}
        )
        self.assertEqual(self.result.files.skipped, 1)
        self.assertEqual(self.result.files.failed, [])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_target_listing_failure_copies_everything(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.side_effect = [
            GraphQLError("target listing boom"),
            iter([{"key": "a.txt", "size": 3}]),
        ]
        mock_download.side_effect = fake_download({"a.txt": b"abc"})

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.copied, [("a.txt", 3)])
        self.assertEqual(self.result.files.skipped, 0)
        self.assertEqual(self.result.files.failed, [])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_walk_failure_keeps_earlier_successes(
        self, mock_walk, mock_download, mock_upload
    ):
        def walk_then_fail():
            yield {"key": "a.txt", "size": 3}
            raise GraphQLError("listing page 2 failed")

        mock_walk.side_effect = fake_walk(walk_then_fail())
        mock_download.side_effect = fake_download({"a.txt": b"abc"})

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.copied, [("a.txt", 3)])
        self.assertEqual(
            self.result.files.failed, [("<listing>", "listing page 2 failed")]
        )


class TransferTest(SimpleTestCase):
    """download/upload against a mock transport, i.e. real httpx plumbing."""

    @patch("hexa.workspace_copier.resources.files.gql")
    def test_download_streams_the_body_into_the_destination(self, mock_gql):
        payload = b"x" * (9 * 1024 * 1024)
        mock_gql.return_value = {
            "prepareObjectDownload": {
                "success": True,
                "errors": [],
                "downloadUrl": "https://storage.test/get",
            }
        }
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, content=payload)
        )

        with (
            httpx.Client(transport=transport) as client,
            tempfile.TemporaryFile() as buffer,
        ):
            written = download(MagicMock(), "src", "big.json", client, buffer)
            buffer.seek(0)
            self.assertEqual(buffer.read(), payload)

        self.assertEqual(written, len(payload))

    @patch("hexa.workspace_copier.resources.files.gql")
    def test_download_error_response_body_is_surfaced(self, mock_gql):
        mock_gql.return_value = {
            "prepareObjectDownload": {
                "success": True,
                "errors": [],
                "downloadUrl": "https://storage.test/get",
            }
        }
        transport = httpx.MockTransport(
            lambda request: httpx.Response(403, text="AccessDenied")
        )

        with (
            httpx.Client(transport=transport) as client,
            tempfile.TemporaryFile() as buffer,
            self.assertRaises(GraphQLError) as ctx,
        ):
            download(MagicMock(), "src", "a.json", client, buffer)

        self.assertIn("403", str(ctx.exception))
        self.assertIn("AccessDenied", str(ctx.exception))

    @patch("hexa.workspace_copier.resources.files.gql")
    def test_upload_sends_content_length_not_chunked(self, mock_gql):
        # Presigned PUT endpoints reject chunked transfer encoding, so httpx
        # must derive a Content-Length from the spool's file descriptor.
        payload = b"y" * (5 * 1024 * 1024)
        mock_gql.return_value = {
            "prepareObjectUpload": {
                "success": True,
                "errors": [],
                "uploadUrl": "https://storage.test/put",
                "headers": {},
            }
        }
        seen = {}

        def handler(request):
            seen["body"] = request.read()
            seen["headers"] = request.headers
            return httpx.Response(200)

        with (
            httpx.Client(transport=httpx.MockTransport(handler)) as client,
            tempfile.TemporaryFile() as buffer,
        ):
            buffer.write(payload)
            buffer.seek(0)
            upload(MagicMock(), "tgt", "a.json", buffer, client)

        self.assertEqual(seen["body"], payload)
        self.assertEqual(seen["headers"]["Content-Length"], str(len(payload)))
        self.assertNotIn("transfer-encoding", seen["headers"])


class IsSkippedTest(SimpleTestCase):
    def test_skips_ipynb_checkpoints_at_any_depth(self):
        self.assertTrue(is_skipped(".ipynb_checkpoints/foo.ipynb"))
        self.assertTrue(is_skipped("notebooks/.ipynb_checkpoints/foo.ipynb"))

    def test_keeps_regular_files(self):
        self.assertFalse(is_skipped("notebooks/foo.ipynb"))
        self.assertFalse(is_skipped("data/a.txt"))


class WalkTest(SimpleTestCase):
    def _page(self, items, has_next=False):
        return {
            "workspace": {
                "bucket": {"objects": {"hasNextPage": has_next, "items": items}}
            }
        }

    @patch("hexa.workspace_copier.resources.files.gql")
    def test_walk_skips_checkpoint_dirs_and_files(self, mock_gql):
        # Top level lists a regular file, a skipped dir, and a normal dir; the
        # skipped dir is never listed (no second gql call for it).
        mock_gql.side_effect = [
            self._page(
                [
                    {"key": "a.txt", "type": "FILE"},
                    {"key": ".ipynb_checkpoints", "type": "DIRECTORY"},
                    {"key": "sub", "type": "DIRECTORY"},
                ]
            ),
            self._page(
                [
                    {"key": "sub/b.txt", "type": "FILE"},
                    {"key": "sub/.ipynb_checkpoints/b.ipynb", "type": "FILE"},
                ]
            ),
        ]

        keys = [obj["key"] for obj in walk(MagicMock(), "src")]

        self.assertEqual(keys, ["a.txt", "sub/b.txt"])
        self.assertEqual(mock_gql.call_count, 2)
