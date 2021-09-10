from logging import getLogger

from dpq.queue import AtLeastOnceQueue

from .models import Database


logger = getLogger(__name__)


def database_sync(queue, job):
    try:
        # permission and db existing are checked by views -> but may change since, so assume failure is possible
        logger.info("start datasource sync, id: %s", job.args["database_id"])
        database = Database.objects.get(id=job.args["database_id"])
        sync_result = database.sync()
        logger.info("end datasource sync id: %s, result: %s", job.args["database_id"], sync_result)
    except:
        logger.exception("database sync failed")


# task queue for the postgresql connector
# AtLeastOnceQueue + try/except: if the worker fail, restart the task. if the task fail, drop it + log
database_sync_queue = AtLeastOnceQueue(
    tasks={
        "database_sync": database_sync,
    },
    notify_channel='database_sync_queue',
)
