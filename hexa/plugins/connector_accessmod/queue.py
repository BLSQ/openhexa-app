from logging import getLogger
from time import sleep

from dpq.queue import AtLeastOnceQueue

from .models import Fileset, FilesetStatus, ValidateFilesetJob

logger = getLogger(__name__)


def validate_fileset_job(queue, job):
    try:
        fileset = Fileset.objects.get(id=job.args["fileset_id"])

    except Fileset.DoesNotExist:
        logger.error("fileset %s not found", job.args["fileset_id"])

    else:
        fileset.status = FilesetStatus.VALIDATING
        fileset.save()

        # a lot of heavy processing...
        sleep(3)

        fileset.status = FilesetStatus.VALID
        fileset.save()


class ValidateFilesetQueue(AtLeastOnceQueue):
    # override the default job model; our job model has a specific table name
    job_model = ValidateFilesetJob


# task queue for the connector_accessmod
# AtLeastOnceQueue + try/except: if the worker fail, restart the task. if the task fail, drop it + log
validate_fileset_queue = ValidateFilesetQueue(
    tasks={
        "validate_fileset": validate_fileset_job,
    },
    notify_channel="validate_fileset_queue",
)
