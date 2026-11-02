from django.test import SimpleTestCase

from hexa.core.text_files.overlay import Overlay


class OverlayTest(SimpleTestCase):
    overlay = Overlay(
        {"a.js": "a", "b.js": "b", "c.js": "c"},
        {"a.js": "changed", "new.js": "new"},
        deleted=["b.js"],
    )

    def test_changes_win_over_base(self):
        self.assertEqual(self.overlay["a.js"], "changed")
        self.assertEqual(self.overlay["c.js"], "c")

    def test_deleted_paths_are_gone(self):
        self.assertNotIn("b.js", self.overlay)
        with self.assertRaises(KeyError):
            self.overlay["b.js"]

    def test_lists_changed_and_remaining_paths_once(self):
        self.assertEqual(sorted(self.overlay), ["a.js", "c.js", "new.js"])
        self.assertEqual(len(self.overlay), 3)

    def test_a_change_restores_a_deleted_path(self):
        overlay = Overlay({"a.js": "a"}, {"a.js": "back"}, deleted=["a.js"])
        self.assertEqual(overlay["a.js"], "back")
