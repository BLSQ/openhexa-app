from unittest.mock import MagicMock

from django.test import SimpleTestCase

from hexa.core.text_files import TextFiles
from hexa.git.exceptions import GitFileTooLarge
from hexa.git.forgejo import MAX_INLINE_BLOB_SIZE
from hexa.git.repo_file_source import GitRepoFileSource

TREE = [
    {"path": "js", "type": "tree"},
    {"path": "index.html", "type": "blob", "size": 11},
    {"path": "js/app.js", "type": "blob", "size": 9},
    {"path": "js/util.js", "type": "blob", "size": 8},
    {"path": "logo.png", "type": "blob", "size": 5},
]
REPO_FILES = [
    {"path": "js", "type": "directory", "content": None, "encoding": None},
    {
        "path": "index.html",
        "type": "file",
        "content": "<h1>hi</h1>",
        "encoding": "TEXT",
    },
    {"path": "js/app.js", "type": "file", "content": "run(app)", "encoding": "TEXT"},
    {"path": "js/util.js", "type": "file", "content": "run(u)", "encoding": "TEXT"},
    {"path": "logo.png", "type": "file", "content": "iVBO", "encoding": "BASE64"},
]


class GitRepoFileSourceTest(SimpleTestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.get_files_tree.return_value = TREE
        self.client.get_repository_files_from_tree.return_value = REPO_FILES
        self.client.get_file.side_effect = lambda repo, path, ref, **kw: {
            "index.html": b"<h1>hi</h1>",
            "js/app.js": b"run(app)",
            "logo.png": b"\x89PNG\x00",
        }[path]

    def _files(self):
        return TextFiles(GitRepoFileSource(self.client, "repo", "main", org_slug="org"))

    def test_glob_only_lists_the_tree(self):
        self.assertEqual(
            self._files().glob("**")["paths"],
            ["index.html", "js/app.js", "js/util.js", "logo.png"],
        )
        self.client.get_file.assert_not_called()
        self.client.get_repository_files_from_tree.assert_not_called()

    def test_read_fetches_that_file_alone(self):
        files = self._files()
        self.assertEqual(files.read("index.html")["content"], "<h1>hi</h1>")
        self.assertEqual(
            files.read("logo.png"), {"error": "Not a readable text file: logo.png"}
        )
        self.client.get_file.assert_any_call(
            "repo", "index.html", "main", org_slug="org"
        )
        self.client.get_repository_files_from_tree.assert_not_called()

    def test_narrow_search_fetches_its_one_file(self):
        result = self._files().grep("run", glob="js/app.*")
        self.assertEqual(result["files"], ["js/app.js"])
        self.client.get_file.assert_called_once()
        self.client.get_repository_files_from_tree.assert_not_called()

    def test_broad_search_loads_every_file_at_once(self):
        result = self._files().grep("run", glob="js/*")
        self.assertEqual(result["files"], ["js/app.js", "js/util.js"])
        self.client.get_file.assert_not_called()
        self.client.get_repository_files_from_tree.assert_called_once_with(
            "repo", TREE, "main", org_slug="org"
        )

    def test_too_large_files_are_none_without_download(self):
        self.client.get_files_tree.return_value = [
            {"path": "huge.js", "type": "blob", "size": MAX_INLINE_BLOB_SIZE},
            {"path": "refused.js", "type": "blob", "size": 10},
        ]
        self.client.get_file.side_effect = GitFileTooLarge("refused.js", 10)
        source = GitRepoFileSource(self.client, "repo", "main")
        self.assertIsNone(source["huge.js"])
        self.assertIsNone(source["refused.js"])
        self.client.get_file.assert_called_once()

    def test_unknown_path(self):
        with self.assertRaises(KeyError):
            GitRepoFileSource(self.client, "repo", "main")["nope.js"]
