from unittest.mock import patch

from django.db import connection
from django.test import TestCase

from hexa.workspace_copier.models import WorkspaceCopyRun, WorkspaceCopyRunStatus
from hexa.workspace_copier.queue import (
    INTERRUPTED_MESSAGE,
    execute_copy_run,
    fail_interrupted_runs,
    workspace_copy_queue,
)
from hexa.workspace_copier.results import CopyResult, FilesResult
from hexa.workspace_copier.service import CredentialError


def _create_run(**overrides):
    data = {
        "source_url": "http://src/graphql/",
        "source_token": "src-secret",
        "source_slug": "my-ws",
        "target_url": "http://tgt/graphql/",
        "target_token": "tgt-secret",
        "target_organization_id": "org-1",
        "resources": ["files", "workspace"],
    }
    data.update(overrides)
    return WorkspaceCopyRun.objects.create(**data)


@patch("hexa.workspace_copier.queue.run_copy")
class ExecuteCopyRunTest(TestCase):
    def assertTokensErased(self, run):
        self.assertIsNone(run.source_token)
        self.assertIsNone(run.target_token)

    def test_success_records_summary_and_erases_tokens(self, mock_run_copy):
        mock_run_copy.return_value = CopyResult(
            workspace_name="My WS", workspace_slug="my-ws-ab12"
        )
        run = _create_run()

        execute_copy_run(str(run.id))

        run.refresh_from_db()
        self.assertEqual(run.status, WorkspaceCopyRunStatus.SUCCESS)
        self.assertEqual(run.result_workspace_slug, "my-ws-ab12")
        self.assertIn("=== Copy summary ===", run.summary)
        self.assertIsNotNone(run.started_at)
        self.assertIsNotNone(run.finished_at)
        self.assertTokensErased(run)

    def test_passes_stored_inputs_to_run_copy(self, mock_run_copy):
        mock_run_copy.return_value = CopyResult()
        run = _create_run(all_dataset_versions=True)

        execute_copy_run(str(run.id))

        kwargs = mock_run_copy.call_args.kwargs
        self.assertEqual(kwargs["source_token"], "src-secret")
        self.assertEqual(kwargs["target_token"], "tgt-secret")
        self.assertEqual(kwargs["resources"], {"files", "workspace"})
        self.assertIsNone(kwargs["target_workspace_slug"])
        self.assertTrue(kwargs["options"].all_dataset_versions)

    def test_partial_failures_mark_success_with_errors(self, mock_run_copy):
        mock_run_copy.return_value = CopyResult(
            files=FilesResult(failed=[("big.zip", "too large")])
        )
        run = _create_run()

        execute_copy_run(str(run.id))

        run.refresh_from_db()
        self.assertEqual(run.status, WorkspaceCopyRunStatus.SUCCESS_WITH_ERRORS)

    def test_credential_error_marks_failed(self, mock_run_copy):
        mock_run_copy.side_effect = CredentialError(
            ["source authentication failed", "target server is unreachable"]
        )
        run = _create_run()

        execute_copy_run(str(run.id))

        run.refresh_from_db()
        self.assertEqual(run.status, WorkspaceCopyRunStatus.FAILED)
        self.assertIn("source authentication failed", run.error)
        self.assertIn("[ERROR] target server is unreachable", run.logs)
        self.assertTokensErased(run)

    def test_unexpected_exception_marks_failed(self, mock_run_copy):
        mock_run_copy.side_effect = RuntimeError("boom")
        run = _create_run()

        with self.assertLogs("hexa.workspace_copier.queue", level="ERROR"):
            execute_copy_run(str(run.id))

        run.refresh_from_db()
        self.assertEqual(run.status, WorkspaceCopyRunStatus.FAILED)
        self.assertEqual(run.error, "boom")
        self.assertIn("Copy failed: boom", run.logs)
        self.assertTokensErased(run)

    def test_logs_written_during_the_run_survive_the_final_save(self, mock_run_copy):
        def fake_copy(**kwargs):
            kwargs["reporter"].info("copied file a.csv")
            return CopyResult()

        mock_run_copy.side_effect = fake_copy
        run = _create_run()

        execute_copy_run(str(run.id))

        run.refresh_from_db()
        self.assertIn("copied file a.csv", run.logs)

    def test_skips_a_run_that_is_not_queued(self, mock_run_copy):
        run = _create_run(status=WorkspaceCopyRunStatus.RUNNING)

        with self.assertLogs("hexa.workspace_copier.queue", level="WARNING"):
            execute_copy_run(str(run.id))

        mock_run_copy.assert_not_called()


class FailInterruptedRunsTest(TestCase):
    def test_marks_running_runs_failed_and_erases_tokens(self):
        running = _create_run(status=WorkspaceCopyRunStatus.RUNNING)

        self.assertEqual(fail_interrupted_runs(), 1)

        running.refresh_from_db()
        self.assertEqual(running.status, WorkspaceCopyRunStatus.FAILED)
        self.assertEqual(running.error, INTERRUPTED_MESSAGE)
        self.assertIn(INTERRUPTED_MESSAGE, running.logs)
        self.assertIsNone(running.source_token)
        self.assertIsNotNone(running.finished_at)

    def test_marks_queued_runs_whose_job_is_gone_failed(self):
        # The worker claimed (and deleted) the job, then crashed before starting.
        orphaned = _create_run()

        self.assertEqual(fail_interrupted_runs(), 1)

        orphaned.refresh_from_db()
        self.assertEqual(orphaned.status, WorkspaceCopyRunStatus.FAILED)
        self.assertEqual(orphaned.error, INTERRUPTED_MESSAGE)
        self.assertIsNone(orphaned.source_token)
        self.assertIsNone(orphaned.target_token)

    def test_leaves_finished_runs_alone(self):
        for status in (
            WorkspaceCopyRunStatus.SUCCESS,
            WorkspaceCopyRunStatus.SUCCESS_WITH_ERRORS,
            WorkspaceCopyRunStatus.FAILED,
        ):
            _create_run(status=status, error="original error")

        self.assertEqual(fail_interrupted_runs(), 0)
        self.assertFalse(
            WorkspaceCopyRun.objects.filter(error=INTERRUPTED_MESSAGE).exists()
        )

    def test_leaves_queued_runs_with_a_job_alone(self):
        queued = _create_run()
        workspace_copy_queue.enqueue("run_workspace_copy", {"run_id": str(queued.id)})

        self.assertEqual(fail_interrupted_runs(), 0)

        queued.refresh_from_db()
        self.assertEqual(queued.status, WorkspaceCopyRunStatus.QUEUED)
        self.assertEqual(queued.source_token, "src-secret")


class TokenStorageTest(TestCase):
    def test_tokens_are_encrypted_in_the_database(self):
        run = _create_run()
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT source_token FROM {WorkspaceCopyRun._meta.db_table} WHERE id = %s",
                [run.id],
            )
            (raw,) = cursor.fetchone()
        self.assertNotIn("src-secret", raw)
