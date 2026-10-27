from django.db import connection
from dpq.commands import Worker

from hexa.workspace_copier.queue import fail_interrupted_runs, workspace_copy_queue

# Any constant works, as long as no other code takes the same advisory lock.
WORKER_LOCK_ID = 17180001


class Command(Worker):
    queue = workspace_copy_queue

    def handle(self, **options):
        # fail_interrupted_runs() is only correct if no other worker is still
        # copying. In a rolling deploy the new worker starts before the old one
        # stops, so wait for the old one's lock first. The lock is held by the
        # database session, so Postgres releases it when the process exits,
        # however it exits; dpq keeps that one connection open for the
        # worker's whole life.
        self.logger.info("Waiting for the workspace copy worker lock...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_lock(%s)", [WORKER_LOCK_ID])
        interrupted = fail_interrupted_runs()
        if interrupted:
            self.logger.warning(
                "Marked %s interrupted workspace copy run(s) as failed.", interrupted
            )
        super().handle(**options)
