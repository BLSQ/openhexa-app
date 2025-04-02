from dpq.commands import Worker

from hexa.plugins.connector_accessmod.queue import validate_fileset_queue


class Command(Worker):
    queue = validate_fileset_queue
