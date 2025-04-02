from logging import getLogger

from django.contrib.contenttypes.models import ContentType
from dpq.queue import AtLeastOnceQueue

from .models import DatasourcesWorkJob

logger = getLogger(__name__)


def datasource_sync(queue, job):
    try:
        # permission and db existing are checked by views -> but may change since, so assume failure is possible
        logger.info(
            "start datasource sync, type: %s, id: %s",
            job.args["contenttype_id"],
            job.args["object_id"],
        )
        datasource_type = ContentType.objects.get_for_id(id=job.args["contenttype_id"])
        datasource = datasource_type.get_object_for_this_type(id=job.args["object_id"])
        sync_result = datasource.sync()
        logger.info(
            "end datasource sync type: %s, id: %s, result: %s",
            job.args["contenttype_id"],
            job.args["object_id"],
            sync_result,
        )
    except Exception:
        logger.exception("datasource sync failed")


def datasource_index(queue, job):
    try:
        datasource_type = ContentType.objects.get_for_id(id=job.args["contenttype_id"])
        datasource = datasource_type.get_object_for_this_type(id=job.args["object_id"])
        datasource.index_all_objects()
    except Exception:
        logger.exception("datasource index failed")


class DatasourcesWorkQueue(AtLeastOnceQueue):
    # override the default job model; our job model has a specific table name
    job_model = DatasourcesWorkJob


# task queue for the postgresql connector
# AtLeastOnceQueue + try/except: if the worker fail, restart the task. if the task fail, drop it + log
datasource_work_queue = DatasourcesWorkQueue(
    tasks={
        "datasource_sync": datasource_sync,
        "datasource_index": datasource_index,
    },
    notify_channel="datasource_work_queue",
)
