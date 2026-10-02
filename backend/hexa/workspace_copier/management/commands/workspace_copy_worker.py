from dpq.commands import Worker

from hexa.workspace_copier.queue import fail_interrupted_runs, workspace_copy_queue


class Command(Worker):
    queue = workspace_copy_queue

    def handle(self, **options):
        interrupted = fail_interrupted_runs()
        if interrupted:
            self.logger.warning(
                "Marked %s interrupted workspace copy run(s) as failed.", interrupted
            )
        super().handle(**options)
