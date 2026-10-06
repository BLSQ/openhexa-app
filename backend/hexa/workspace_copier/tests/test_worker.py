from unittest.mock import patch

from django.db import connection
from django.test import TestCase
from dpq.commands import Worker

from hexa.workspace_copier.management.commands.workspace_copy_worker import (
    WORKER_LOCK_ID,
    Command,
)


def _holds_worker_lock() -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_locks WHERE locktype = 'advisory'"
            " AND objid = %s AND pid = pg_backend_pid() AND granted)",
            [WORKER_LOCK_ID],
        )
        return cursor.fetchone()[0]


@patch.object(Worker, "handle")
class WorkspaceCopyWorkerTest(TestCase):
    def setUp(self):
        # The lock belongs to the session, not the test transaction, so it
        # would outlive the test without this.
        self.addCleanup(self._release_lock)

    def _release_lock(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_unlock_all()")

    def test_takes_the_lock_before_failing_interrupted_runs(self, mock_handle):
        lock_held_during_cleanup = []

        def fake_fail_interrupted_runs():
            lock_held_during_cleanup.append(_holds_worker_lock())
            return 0

        with patch(
            "hexa.workspace_copier.management.commands.workspace_copy_worker.fail_interrupted_runs",
            side_effect=fake_fail_interrupted_runs,
        ):
            Command().handle(delay=1, listen=False)

        self.assertEqual(lock_held_during_cleanup, [True])
        mock_handle.assert_called_once()
