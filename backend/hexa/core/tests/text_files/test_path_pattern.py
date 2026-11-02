from django.test import SimpleTestCase

from hexa.core.text_files import PathPattern


class PathPatternTest(SimpleTestCase):
    def test_star_stays_in_directory(self):
        self.assertTrue(PathPattern("*.js").matches("app.js"))
        self.assertFalse(PathPattern("*.js").matches("lib/app.js"))

    def test_double_star_spans_any_depth(self):
        pattern = PathPattern("src/**/*.ts")
        self.assertTrue(pattern.matches("src/main.ts"))
        self.assertTrue(pattern.matches("src/lib/util.ts"))
        self.assertFalse(pattern.matches("main.ts"))

    def test_matches_hidden_files(self):
        self.assertTrue(PathPattern("**/*.js").matches(".config/app.js"))

    def test_braces_expand_alternatives(self):
        pattern = PathPattern("**/*.{html,css}")
        self.assertTrue(pattern.matches("index.html"))
        self.assertTrue(pattern.matches("css/style.css"))
        self.assertFalse(pattern.matches("app.js"))
