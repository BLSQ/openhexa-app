from dpq.commands import Worker

from hexa.datasets.queue import dataset_file_metadata_queue


class Command(Worker):
    queue = dataset_file_metadata_queue
