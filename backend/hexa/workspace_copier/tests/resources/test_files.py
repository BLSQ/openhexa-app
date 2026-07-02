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
    def test_skip_existing_skips_matching_key_and_size(
        self, mock_walk, mock_download, mock_upload
    ):
        # First walk() call lists the target, second walks the source.
        # 'same.txt' matches key+size and is skipped; 'grew.txt' exists but
        # with a different size so it is re-copied; 'new.txt' is absent.
        mock_walk.side_effect = [
            iter([{"key": "same.txt", "size": 3}, {"key": "grew.txt", "size": 1}]),
            iter(
                [
                    {"key": "same.txt", "size": 3},
                    {"key": "grew.txt", "size": 5},
                    {"key": "new.txt", "size": 2},
                ]
            ),
        ]
        contents = {"grew.txt": b"12345", "new.txt": b"12"}
        mock_download.side_effect = lambda client, slug, path, http_client: contents[
            path
        ]

        FilesCopier(skip_existing=True).copy(
            self.source, self.target, self.result, NullReporter()
        )

        self.assertEqual(
            set(self.result.files.copied), {("grew.txt", 5), ("new.txt", 2)}
        )
        self.assertEqual(self.result.files.skipped, 1)
        self.assertEqual(self.result.files.failed, [])

    @patch("hexa.workspace_copier.resources.files.upload")
    @patch("hexa.workspace_copier.resources.files.download")
    @patch("hexa.workspace_copier.resources.files.walk")
    def test_skip_existing_target_listing_failure_copies_everything(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.side_effect = [
            GraphQLError("target listing boom"),
            iter([{"key": "a.txt", "size": 3}]),
        ]
        mock_download.side_effect = [b"abc"]

        FilesCopier(skip_existing=True).copy(
            self.source, self.target, self.result, NullReporter()
        )

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

    @patch("hexa.workspace_copier.resources.files.gql")
    def test_walk_only_dirs_keeps_root_folders_and_prunes_the_rest(self, mock_gql):
        # Only the root 'data' folder is walked: root-level files are pruned —
        # even one named exactly like an only-folder ('readme') — and so is
        # the 'other' dir (no listing call for it), so a nested 'other/data'
        # would never be reached.
        mock_gql.side_effect = [
            self._page(
                [
                    {"key": "a.txt", "type": "FILE"},
                    {"key": "readme", "type": "FILE"},
                    {"key": "data", "type": "DIRECTORY"},
                    {"key": "other", "type": "DIRECTORY"},
                ]
            ),
            self._page(
                [
                    {"key": "data/b.txt", "type": "FILE"},
                    {"key": "data/nested", "type": "DIRECTORY"},
                ]
            ),
            self._page([{"key": "data/nested/c.txt", "type": "FILE"}]),
        ]

        keys = [
            obj["key"]
            for obj in walk(MagicMock(), "src", only_dirs=frozenset({"data", "readme"}))
        ]

        self.assertEqual(keys, ["data/b.txt", "data/nested/c.txt"])
        self.assertEqual(mock_gql.call_count, 3)
