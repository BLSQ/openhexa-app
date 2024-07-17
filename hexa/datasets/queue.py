from logging import getLogger

from dpq.queue import AtLeastOnceQueue

from hexa.datasets.models import DatasetFileMetadataJob

logger = getLogger(__name__)


def generate_dataset_file_sample_task(
    queue: AtLeastOnceQueue, job: DatasetFileMetadataJob
):
    # TODO: imlpement ticket PATHWAYS-98  - extract data in background task
    dataset_version_file_id = job.args["fileId"]
    logger.info(f"Creating dataset version file {dataset_version_file_id}")


class DatasetsFileMetadataQueue(AtLeastOnceQueue):
    job_model = DatasetFileMetadataJob


dataset_file_metadata_queue = DatasetsFileMetadataQueue(
    tasks={
        "generate_file_sample": generate_dataset_file_sample_task,
    },
    notify_channel="dataset_file_metadata_queue",
)
