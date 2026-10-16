from django.test import SimpleTestCase

from hexa.core.text_files.window import read_window

TEXT = "one\ntwo\nthree\nfour\n"


class ReadWindowTest(SimpleTestCase):
    def test_whole_text(self):
        self.assertEqual(
            read_window(TEXT),
            {
                "start_line": 1,
                "end_line": 4,
                "total_lines": 4,
                "content": "one\ntwo\nthree\nfour",
            },
        )

    def test_window_with_line_numbers(self):
        result = read_window(TEXT, 2, 3, line_numbers=True)
        self.assertEqual(result["content"], "     2\ttwo\n     3\tthree")

    def test_max_lines_returns_partial_view(self):
        result = read_window(TEXT, max_lines=2)
        self.assertEqual(result["content"], "one\ntwo")
        self.assertEqual(result["end_line"], 2)
        self.assertIn("PARTIAL view: lines 1-2 of 4", result["notice"])

    def test_max_line_chars_clips(self):
        result = read_window("abcdef", max_line_chars=3)
        self.assertEqual(result["content"], "abc… [3 more characters]")

    def test_empty_text(self):
        self.assertEqual(read_window("")["notice"], "The file is empty.")

    def test_start_past_end(self):
        result = read_window(TEXT, 10)
        self.assertEqual(result["content"], "")
        self.assertIn("past the end of the file (4 lines)", result["notice"])
