from dpq.commands import Worker

from hexa.datasets.queue import dataset_snapshot_queue


class Command(Worker):
    queue = dataset_snapshot_queue
