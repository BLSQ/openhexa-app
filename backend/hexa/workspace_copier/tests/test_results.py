from django.test import SimpleTestCase

from hexa.workspace_copier.results import (
    CopyResult,
    FilesResult,
    format_bytes,
    format_summary,
)


class FormatBytesTest(SimpleTestCase):
    def test_small_sizes_stay_exact(self):
        self.assertEqual(format_bytes(0), "0 B")
        self.assertEqual(format_bytes(512), "512 B")
        self.assertEqual(format_bytes(1023), "1023 B")

    def test_scales_to_binary_units(self):
        self.assertEqual(format_bytes(1024), "1.0 KiB")
        self.assertEqual(format_bytes(897862356), "856.3 MiB")
        self.assertEqual(format_bytes(1437567641), "1.3 GiB")
        self.assertEqual(format_bytes(7401049609), "6.9 GiB")

    def test_caps_at_the_largest_known_unit(self):
        self.assertEqual(format_bytes(5 * 1024**6), "5120.0 PiB")


class FormatSummaryTest(SimpleTestCase):
    def test_copied_total_is_human_readable(self):
        result = CopyResult(
            workspace_name="Big", workspace_slug="big-ab12", files=FilesResult()
        )
        result.files.copied = [("a.json", 1437567641), ("b.json", 1024)]

        self.assertIn("Files copied: 2 (1.3 GiB)", format_summary(result))
