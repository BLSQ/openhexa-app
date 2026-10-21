from django.test import SimpleTestCase

from hexa.core.text_files import GrepOutputMode, ReadOptions, TextFiles


class _ReadLog(dict):
    """A file mapping that records which contents were read, like a lazy source would."""

    def __init__(self, *args):
        super().__init__(*args)
        self.reads = []

    def __getitem__(self, path):
        self.reads.append(path)
        return super().__getitem__(path)


class TextFilesGlobTest(SimpleTestCase):
    files = TextFiles(
        dict.fromkeys(
            ["index.html", "app.js", "css/style.css", "src/lib/util.ts", "src/main.ts"],
            "",
        )
    )

    def test_returns_sorted_matches(self):
        self.assertEqual(
            self.files.glob("**/*.ts"),
            {"paths": ["src/lib/util.ts", "src/main.ts"], "truncated": False},
        )

    def test_limit_flags_truncation(self):
        self.assertEqual(
            self.files.glob("**", limit=2),
            {"paths": ["app.js", "css/style.css"], "truncated": True},
        )


class TextFilesGrepTest(SimpleTestCase):
    def test_glob_scopes_files(self):
        files = TextFiles({"app.js": "a", "style.css": "a"})
        self.assertEqual(files.grep("a", glob="*.js")["files"], ["app.js"])

    def test_glob_filter_skips_reading_other_files(self):
        files = _ReadLog({"app.js": "a", "style.css": "a"})
        TextFiles(files).grep("a", glob="*.js")
        self.assertEqual(files.reads, ["app.js"])

    def test_skips_unreadable_files(self):
        files = TextFiles({"app.js": "png", "logo.png": None})
        self.assertEqual(files.grep("png")["files"], ["app.js"])

    def test_stops_reading_once_page_is_filled(self):
        files = _ReadLog({f"{i}.txt": "match" for i in range(10)})
        result = TextFiles(files).grep("match", head_limit=2)
        self.assertEqual(result["files"], ["0.txt", "1.txt"])
        self.assertTrue(result["truncated"])
        self.assertEqual(files.reads, ["0.txt", "1.txt", "2.txt"])

    def test_count_reads_every_file(self):
        files = _ReadLog({f"{i}.txt": "match" for i in range(10)})
        result = TextFiles(files).grep(
            "match", output_mode=GrepOutputMode.COUNT, head_limit=2
        )
        self.assertEqual(result["total"], 10)
        self.assertEqual(len(files.reads), 10)

    def test_should_stop_ends_the_search_before_the_next_read(self):
        files = _ReadLog({f"{i}.txt": "match" for i in range(10)})
        result = TextFiles(files).grep(
            "match",
            output_mode=GrepOutputMode.COUNT,
            should_stop=lambda: len(files.reads) == 3,
        )
        self.assertEqual(files.reads, ["0.txt", "1.txt", "2.txt"])
        self.assertEqual(result["total"], 3)
        self.assertTrue(result["truncated"])
        self.assertEqual(
            result["notice"],
            "Search stopped after 3 of 10 files, so results are partial: narrow the search.",
        )

    def test_should_stop_unused_when_the_page_fills_first(self):
        files = _ReadLog({f"{i}.txt": "match" for i in range(10)})
        result = TextFiles(files).grep(
            "match", head_limit=2, should_stop=lambda: len(files.reads) == 5
        )
        self.assertEqual(result["files"], ["0.txt", "1.txt"])
        self.assertNotIn("notice", result)


class TextFilesReadTest(SimpleTestCase):
    files = TextFiles({"f.txt": "one\ntwo\nthree\n"})

    def test_reads_window(self):
        result = self.files.read("f.txt", 2, 2, ReadOptions(line_numbers=True))
        self.assertEqual(result["content"], "     2\ttwo")
        self.assertEqual(result["total_lines"], 3)

    def test_unreadable_file(self):
        files = TextFiles({"logo.png": None})
        self.assertEqual(
            files.read("logo.png"), {"error": "Not a readable text file: logo.png"}
        )

    def test_missing_file(self):
        self.assertEqual(
            self.files.read("nope.txt"), {"error": "File not found: nope.txt"}
        )


class TextFilesWithChangesTest(SimpleTestCase):
    def test_reads_through_changes_and_deletions(self):
        files = TextFiles({"a.js": "old", "b.js": "b"}).with_changes(
            {"a.js": "new"}, deleted=["b.js"]
        )
        self.assertEqual(files.read("a.js")["content"], "new")
        self.assertEqual(files.glob("**")["paths"], ["a.js"])
