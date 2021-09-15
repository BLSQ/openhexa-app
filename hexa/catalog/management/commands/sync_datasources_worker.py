from dpq.commands import Worker

from hexa.catalog.queue import datasource_sync_queue


class Command(Worker):
    queue = datasource_sync_queue
