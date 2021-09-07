from dpq.commands import Worker

from hexa.plugins.connector_postgresql.queue import database_sync_queue


class Command(Worker):
    queue = database_sync_queue
