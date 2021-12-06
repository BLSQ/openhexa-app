from logging import getLogger

from django.contrib.contenttypes.models import ContentType
from dpq.queue import AtLeastOnceQueue

from .models import EnvironmentsSyncJob

logger = getLogger(__name__)


def environment_sync(queue, job):
    try:
        # permission and db existing are checked by views -> but may change since, so assume failure is possible
        logger.info(
            "start environment sync, type: %s, id: %s",
            job.args["contenttype_id"],
            job.args["object_id"],
        )
        environment_type = ContentType.objects.get_for_id(id=job.args["contenttype_id"])
        environment = environment_type.get_object_for_this_type(
            id=job.args["object_id"]
        )
        sync_result = environment.sync()
        logger.info(
            "end environment sync type: %s, id: %s, result: %s",
            job.args["contenttype_id"],
            job.args["object_id"],
            sync_result,
        )
    except Exception:
        logger.exception("environment sync failed")


class EnvironmentsSyncQueue(AtLeastOnceQueue):
    job_model = EnvironmentsSyncJob


# task queue for all the connectors providing environment running pipelines (airflow, ...)
# AtLeastOnceQueue + try/except: if the worker fail, restart the task. if the task fail, drop it + log
environment_sync_queue = EnvironmentsSyncQueue(
    tasks={
        "environment_sync": environment_sync,
    },
    notify_channel="environment_sync_queue",
)
