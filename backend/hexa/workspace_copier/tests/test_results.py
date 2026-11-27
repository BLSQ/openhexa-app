from django.test import SimpleTestCase

from hexa.workspace_copier.results import (
    ConnectionsResult,
    CopyResult,
    DatabaseResult,
    FilesResult,
    PipelinesResult,
    StepStatus,
    WebappsResult,
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


class HasFailuresTest(SimpleTestCase):
    def test_false_when_nothing_failed(self):
        result = CopyResult(files=FilesResult(skipped=3), pipelines=PipelinesResult())
        self.assertFalse(result.has_failures)

    def test_true_when_any_resource_failed(self):
        result = CopyResult(pipelines=PipelinesResult(failed=["etl"]))
        self.assertTrue(result.has_failures)

    def test_true_when_a_webapp_failed(self):
        result = CopyResult(webapps=WebappsResult(failed=["app"]))
        self.assertTrue(result.has_failures)


class StepStatusTest(SimpleTestCase):
    def test_a_resource_without_problems_succeeds(self):
        result = CopyResult(files=FilesResult(copied=[("a.csv", 3)]))

        self.assertEqual(StepStatus.SUCCESS, result.step_status("files"))
        self.assertEqual(StepStatus.SUCCESS, result.step_status("workspace"))

    def test_warnings_and_failures_are_told_apart(self):
        result = CopyResult(
            pipelines=PipelinesResult(warnings=["schedule not copied"]),
            datasets=None,
            webapps=WebappsResult(failed=["app"], warnings=["app failed"]),
        )

        self.assertEqual(
            StepStatus.SUCCESS_WITH_WARNINGS, result.step_status("pipelines")
        )
        self.assertEqual(StepStatus.SUCCESS_WITH_ERRORS, result.step_status("webapps"))

    def test_web_app_notes_are_not_warnings(self):
        result = CopyResult(webapps=WebappsResult(created=["app"], notes=["note"]))

        self.assertEqual(StepStatus.SUCCESS, result.step_status("webapps"))
        self.assertEqual([], result.all_warnings())

    def test_a_database_not_copied_is_failed_or_skipped(self):
        failed = CopyResult(database=DatabaseResult(failed="in use"))
        skipped = CopyResult(database=DatabaseResult(skipped="not empty"))

        self.assertEqual(StepStatus.FAILED, failed.step_status("database"))
        self.assertEqual(
            StepStatus.SUCCESS_WITH_WARNINGS, skipped.step_status("database")
        )


class AllWarningsTest(SimpleTestCase):
    def test_gathers_every_resource_and_logged_only_failures(self):
        result = CopyResult(
            warnings=["run warning"],
            files=FilesResult(failed=[("a.csv", "timeout"), ("b.csv", "timeout")]),
            database=DatabaseResult(failed="in use"),
            connections=ConnectionsResult(failed=["dhis2"], warnings=["empty secret"]),
            pipelines=PipelinesResult(warnings=["schedule not copied"]),
        )

        self.assertEqual(
            [
                "run warning",
                "2 file(s) could not be copied — see the logs for the list.",
                "The database was not copied: in use",
                "empty secret",
                "connection 'dhis2' could not be created — handle manually.",
                "schedule not copied",
            ],
            result.all_warnings(),
        )
