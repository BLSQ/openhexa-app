from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from hexa.workspace_duplicator.endpoints import Endpoint
from hexa.workspace_duplicator.progress import NullReporter
from hexa.workspace_duplicator.resources.files import FilesCopier
from hexa.workspace_duplicator.results import DuplicationResult
from hexa.workspace_duplicator.transport import GraphQLError


class FilesCopierRemoteTest(SimpleTestCase):
    def setUp(self):
        self.source = Endpoint.remote(MagicMock(), "src")
        self.target = Endpoint.remote(MagicMock(), "tgt")
        self.result = DuplicationResult()

    @patch("hexa.workspace_duplicator.resources.files.upload")
    @patch("hexa.workspace_duplicator.resources.files.download")
    @patch("hexa.workspace_duplicator.resources.files.walk")
    def test_copies_each_file(self, mock_walk, mock_download, mock_upload):
        mock_walk.return_value = iter(
            [{"key": "a.txt", "size": 3}, {"key": "dir/b.txt", "size": 5}]
        )
        mock_download.side_effect = [b"abc", b"hello"]

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.copied, [("a.txt", 3), ("dir/b.txt", 5)])
        self.assertEqual(mock_upload.call_count, 2)

    @patch("hexa.workspace_duplicator.resources.files.upload")
    @patch("hexa.workspace_duplicator.resources.files.download")
    @patch("hexa.workspace_duplicator.resources.files.walk")
    def test_failed_file_is_recorded_and_loop_continues(
        self, mock_walk, mock_download, mock_upload
    ):
        mock_walk.return_value = iter(
            [{"key": "bad.txt", "size": 1}, {"key": "ok.txt", "size": 2}]
        )
        mock_download.side_effect = [GraphQLError("boom"), b"ok"]

        FilesCopier().copy(self.source, self.target, self.result, NullReporter())

        self.assertEqual(self.result.files.failed, ["bad.txt"])
        self.assertEqual(self.result.files.copied, [("ok.txt", 2)])
