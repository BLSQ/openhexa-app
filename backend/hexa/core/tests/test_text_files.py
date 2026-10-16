from django.test import SimpleTestCase

from hexa.core.text_files import GrepOutputMode, PathPattern, TextFiles


class PathPatternTest(SimpleTestCase):
    def test_star_stays_in_directory(self):
        self.assertTrue(PathPattern("*.js").matches("app.js"))
        self.assertFalse(PathPattern("*.js").matches("lib/app.js"))

    def test_double_star_spans_any_depth(self):
        pattern = PathPattern("src/**/*.ts")
        self.assertTrue(pattern.matches("src/main.ts"))
        self.assertTrue(pattern.matches("src/lib/util.ts"))
        self.assertFalse(pattern.matches("main.ts"))

    def test_braces_expand_alternatives(self):
        pattern = PathPattern("**/*.{html,css}")
        self.assertTrue(pattern.matches("index.html"))
        self.assertTrue(pattern.matches("css/style.css"))
        self.assertFalse(pattern.matches("app.js"))


class GlobTest(SimpleTestCase):
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


class GrepTest(SimpleTestCase):
    files = TextFiles(
        {
            "app.js": "const a = 1;\nfunction render() {\n  return a;\n}\n",
            "index.html": "<div id='app'></div>\n<script src='app.js'></script>\n",
            "style.css": "body { margin: 0; }\n",
        }
    )

    def test_files_with_matches_is_default(self):
        self.assertEqual(self.files.grep("app")["files"], ["index.html"])

    def test_glob_scopes_files(self):
        self.assertEqual(self.files.grep("a", glob="*.js")["files"], ["app.js"])

    def test_ignore_case(self):
        self.assertEqual(self.files.grep("RENDER")["files"], [])
        self.assertEqual(
            self.files.grep("RENDER", ignore_case=True)["files"], ["app.js"]
        )

    def test_content_has_line_numbers_and_context(self):
        result = self.files.grep(
            "render", output_mode=GrepOutputMode.CONTENT, context=1
        )
        self.assertEqual(
            result["content"],
            "app.js-1-const a = 1;\napp.js:2:function render() {\napp.js-3-  return a;",
        )

    def test_content_separates_non_contiguous_groups(self):
        result = TextFiles({"f.txt": "x\n1\n2\n3\nx\n"}).grep(
            "x", output_mode=GrepOutputMode.CONTENT
        )
        self.assertEqual(result["content"], "f.txt:1:x\n--\nf.txt:5:x")

    def test_content_clips_long_lines(self):
        result = TextFiles({"min.js": "a" * 1000}).grep(
            "a", output_mode=GrepOutputMode.CONTENT
        )
        self.assertIn("[700 more characters]", result["content"])

    def test_count_total_covers_all_matches_despite_paging(self):
        result = self.files.grep("a", output_mode=GrepOutputMode.COUNT, head_limit=1)
        self.assertEqual(result["counts"], {"app.js": 2})
        self.assertEqual(result["total"], 5)
        self.assertTrue(result["truncated"])

    def test_offset_past_matches_returns_notice(self):
        result = self.files.grep("a", offset=10)
        self.assertEqual(result["files"], [])
        self.assertIn("No entries at offset 10", result["notice"])

    def test_invalid_regex_returns_error(self):
        self.assertIn("Invalid regular expression", self.files.grep("(")["error"])


class ReadTest(SimpleTestCase):
    files = TextFiles({"f.txt": "one\ntwo\nthree\nfour\n", "empty.txt": ""})

    def test_whole_file(self):
        self.assertEqual(
            self.files.read("f.txt"),
            {
                "start_line": 1,
                "end_line": 4,
                "total_lines": 4,
                "content": "one\ntwo\nthree\nfour",
            },
        )

    def test_window_with_line_numbers(self):
        result = self.files.read("f.txt", 2, 3, line_numbers=True)
        self.assertEqual(result["content"], "     2\ttwo\n     3\tthree")

    def test_max_lines_returns_partial_view(self):
        result = self.files.read("f.txt", max_lines=2)
        self.assertEqual(result["content"], "one\ntwo")
        self.assertEqual(result["end_line"], 2)
        self.assertIn("PARTIAL view: lines 1-2 of 4", result["notice"])

    def test_max_line_chars_clips(self):
        result = TextFiles({"f.txt": "abcdef"}).read("f.txt", max_line_chars=3)
        self.assertEqual(result["content"], "abc… [3 more characters]")

    def test_empty_file(self):
        self.assertEqual(self.files.read("empty.txt")["notice"], "The file is empty.")

    def test_start_past_end(self):
        result = self.files.read("f.txt", 10)
        self.assertEqual(result["content"], "")
        self.assertIn("past the end of the file (4 lines)", result["notice"])

    def test_missing_file(self):
        self.assertEqual(
            self.files.read("nope.txt"), {"error": "File not found: nope.txt"}
        )
