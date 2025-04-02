from dpq.commands import Worker

from hexa.catalog.queue import datasource_work_queue


class Command(Worker):
    queue = datasource_work_queue
