from unittest.mock import MagicMock, patch

import httpx
from django.test import SimpleTestCase

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.files import FilesCopier, is_skipped, walk
from hexa.workspace_copier.results import CopyResult
from hexa.workspace_copier.transport import GraphQLError


class FilesCopierRemoteTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.result = CopyResult()

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_copies_each_file(self, mock_walk, mock_download, mock_upload):
        mock_walk.return_value = iter(
            [{"key": "a.txt", "size": 3}, {"key": "dir/b.txt", "size": 5}]
        )
        mock_download.side_effect = [b"abc", b"hello"]

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.copied, [("a.txt", 3), ("dir/b.txt", 5)])
        self.assertEqual(mock_upload.call_count, 2)

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_failed_file_is_recorded_and_loop_continues(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.return_value = iter(
            [{"key": "bad.txt", "size": 1}, {"key": "ok.txt", "size": 2}]
        )
        mock_download.side_effect = [GraphQLError("boom"), b"ok"]

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.failed, [("bad.txt", "GraphQLError: boom")])
        self.assertEqual(self.result.files.copied, [("ok.txt", 2)])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_httpx_error_during_transfer_is_recorded_and_loop_continues(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.return_value = iter(
            [{"key": "bad.txt", "size": 1}, {"key": "ok.txt", "size": 2}]
        )
        mock_download.side_effect = [httpx.ReadTimeout("blip"), b"ok"]

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.failed, [("bad.txt", "ReadTimeout: blip")])
        self.assertEqual(self.result.files.copied, [("ok.txt", 2)])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_walk_failure_keeps_earlier_successes(
        self, mock_walk, mock_download, mock_upload
    ):
        def walk_then_fail():
            yield {"key": "a.txt", "size": 3}
            raise GraphQLError("listing page 2 failed")

        mock_walk.return_value = walk_then_fail()
        mock_download.side_effect = [b"abc"]

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.copied, [("a.txt", 3)])
        self.assertEqual(
            self.result.files.failed, [("<listing>", "listing page 2 failed")]
        )


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
