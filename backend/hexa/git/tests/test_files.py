from django.test import SimpleTestCase

from hexa.git.exceptions import GitFileTooLarge
from hexa.git.files import MAX_TEXT_FILE_SIZE, GitFiles, decode_text
from hexa.git.testutils import make_git_client_mock


class DecodeTextTest(SimpleTestCase):
    def test_text(self):
        self.assertEqual(decode_text("héllo".encode()), "héllo")

    def test_binary(self):
        self.assertIsNone(decode_text(b"\x89PNG\x00"))
        self.assertIsNone(decode_text(b"\xff\xfe"))


class GitFilesTest(SimpleTestCase):
    def setUp(self):
        self.client = make_git_client_mock()
        self.client.get_files_tree.return_value = [
            {"path": "src", "type": "tree"},
            {"path": "src/app.js", "type": "blob", "size": 5},
            {"path": "logo.png", "type": "blob", "size": 4},
            {"path": "big.json", "type": "blob", "size": MAX_TEXT_FILE_SIZE + 1},
        ]
        self.files = GitFiles(self.client, "repo", "main", "org")

    def test_lists_blobs_without_fetching_contents(self):
        self.assertEqual(sorted(self.files), ["big.json", "logo.png", "src/app.js"])
        self.assertIn("src/app.js", self.files)
        self.assertNotIn("src", self.files)
        self.client.get_file.assert_not_called()

    def test_fetches_text_once(self):
        self.client.get_file.return_value = b"app()"
        self.assertEqual(self.files["src/app.js"], "app()")
        self.assertEqual(self.files["src/app.js"], "app()")
        self.client.get_file.assert_called_once_with(
            "repo", "src/app.js", "main", org_slug="org"
        )

    def test_binary_and_oversized_files_are_none(self):
        self.client.get_file.return_value = b"\x89PNG\x00"
        self.assertIsNone(self.files["logo.png"])
        self.assertIsNone(self.files["big.json"])
        self.client.get_file.assert_called_once()

    def test_file_too_large_for_the_server_is_none(self):
        self.client.get_file.side_effect = GitFileTooLarge("src/app.js", 5)
        self.assertIsNone(self.files["src/app.js"])

    def test_unknown_path(self):
        with self.assertRaises(KeyError):
            self.files["nope.js"]
