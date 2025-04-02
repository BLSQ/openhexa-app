from dpq.commands import Worker

from hexa.pipelines.queue import environment_sync_queue


class Command(Worker):
    queue = environment_sync_queue
