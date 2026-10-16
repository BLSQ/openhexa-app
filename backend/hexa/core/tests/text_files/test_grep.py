from django.test import SimpleTestCase

from hexa.core.text_files.grep import GrepOutputMode, grep

FILES = [
    ("app.js", "const a = 1;\nfunction render() {\n  return a;\n}\n"),
    ("index.html", "<div id='app'></div>\n<script src='app.js'></script>\n"),
    ("style.css", "body { margin: 0; }\n"),
]


class GrepTest(SimpleTestCase):
    def test_files_with_matches_is_default(self):
        self.assertEqual(grep(FILES, "app")["files"], ["index.html"])

    def test_ignore_case(self):
        self.assertEqual(grep(FILES, "RENDER")["files"], [])
        self.assertEqual(grep(FILES, "RENDER", ignore_case=True)["files"], ["app.js"])

    def test_content_has_line_numbers_and_context(self):
        result = grep(FILES, "render", output_mode=GrepOutputMode.CONTENT, context=1)
        self.assertEqual(
            result["content"],
            "app.js-1-const a = 1;\napp.js:2:function render() {\napp.js-3-  return a;",
        )

    def test_content_separates_non_contiguous_groups(self):
        result = grep(
            [("f.txt", "x\n1\n2\n3\nx\n")], "x", output_mode=GrepOutputMode.CONTENT
        )
        self.assertEqual(result["content"], "f.txt:1:x\n--\nf.txt:5:x")

    def test_content_clips_long_lines(self):
        result = grep([("min.js", "a" * 1000)], "a", output_mode=GrepOutputMode.CONTENT)
        self.assertIn("[700 more characters]", result["content"])

    def test_count_total_covers_all_matches_despite_paging(self):
        result = grep(FILES, "a", output_mode=GrepOutputMode.COUNT, head_limit=1)
        self.assertEqual(result["counts"], {"app.js": 2})
        self.assertEqual(result["total"], 5)
        self.assertTrue(result["truncated"])

    def test_offset_past_matches_returns_notice(self):
        result = grep(FILES, "a", offset=10)
        self.assertEqual(result["files"], [])
        self.assertIn("No entries at offset 10", result["notice"])

    def test_line_anchors(self):
        self.assertEqual(grep(FILES, r"^function")["files"], ["app.js"])
        self.assertEqual(grep(FILES, r"\Afunction")["files"], ["app.js"])

    def test_match_across_lines_is_not_reported(self):
        self.assertEqual(grep([("f.txt", "a\nb\n")], r"a\sb")["files"], [])

    def test_invalid_regex_returns_error(self):
        self.assertIn("Invalid regular expression", grep(FILES, "(")["error"])
