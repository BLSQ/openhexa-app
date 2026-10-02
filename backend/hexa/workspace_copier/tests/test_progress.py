from django.test import TestCase

from hexa.workspace_copier.models import WorkspaceCopyRun
from hexa.workspace_copier.progress import DatabaseReporter


class DatabaseReporterTest(TestCase):
    def setUp(self):
        self.run = WorkspaceCopyRun.objects.create(source_slug="my-ws")

    def _logs(self):
        self.run.refresh_from_db()
        return self.run.logs

    def test_buffers_info_lines_until_batch_is_full(self):
        reporter = DatabaseReporter(self.run, flush_interval=3600, max_buffer=3)
        reporter.info("one")
        reporter.info("two")
        self.assertEqual(self._logs(), "")

        reporter.info("three")
        lines = self._logs().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[2].endswith("three"))

    def test_warning_and_error_flush_immediately(self):
        reporter = DatabaseReporter(self.run, flush_interval=3600, max_buffer=50)
        reporter.info("before")
        reporter.warning("careful")
        self.assertIn("before", self._logs())
        self.assertIn("[WARNING] careful", self._logs())

        reporter.error("broken")
        self.assertIn("[ERROR] broken", self._logs())

    def test_flush_appends_to_existing_logs(self):
        WorkspaceCopyRun.objects.filter(pk=self.run.pk).update(logs="earlier\n")
        reporter = DatabaseReporter(self.run, flush_interval=3600)
        reporter.info("later")
        reporter.flush()
        self.assertTrue(self._logs().startswith("earlier\n"))
        self.assertIn("later", self._logs())

    def test_flush_with_empty_buffer_does_not_query(self):
        reporter = DatabaseReporter(self.run)
        with self.assertNumQueries(0):
            reporter.flush()
