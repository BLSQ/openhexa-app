from logging import getLogger

from dpq.queue import AtLeastOnceQueue

from hexa.datasets.models import DatasetFileMetadataJob
from hexa.datasets.models import (
    DatasetFileSnapshot,
    DatasetVersionFile,
)
from hexa.files.api import get_storage

logger = getLogger(__name__)

# qdd to settings
DEFAULT_SNAPSHOT_LINES = 50


def generate_dataset_file_sample_task(queue: AtLeastOnceQueue, job: DatasetSnapshotJob):
    try:
        dataset_version_file_id = job.args["file_id"]
        dataset_version_file = DatasetVersionFile.objects.get(
            id=dataset_version_file_id
        )
        logger.info(
            f"Creating dataset snapshot for version file {dataset_version_file_id}"
        )
        dataset_file_snapshot = DatasetFileSnapshot.objects.create(
            dataset_version_file=dataset_version_file,
            status=DatasetFileSnapshot.STATUS_PROCESSING,
        )

        storage = get_storage()
        dataset_snapshot_content = storage.read_object_lines(
            dataset_version_file, DEFAULT_SNAPSHOT_LINES
        )
        dataset_file_snapshot.content = dataset_snapshot_content
        dataset_file_snapshot.status = DatasetFileSnapshot.STATUS_FINISHED
        dataset_file_snapshot.save()
        logger.info("Dataset snapshot created for file {dataset_version_file_id}")
    except Exception as e:
        dataset_version_file_id = job.args["file_id"]
        dataset_version_file = DatasetVersionFile.objects.get(
            id=dataset_version_file_id
        )
        dataset_file_snapshot = DatasetFileSnapshot.objects.get(
            dataset_version_file=dataset_version_file
        )
        dataset_file_snapshot.status = DatasetFileSnapshot.STATUS_FAILED
        dataset_file_snapshot.save()
        logger.exception(f"Failed to create dataset snapshot: \n {e}")


class DatasetsFileMetadataQueue(AtLeastOnceQueue):
    job_model = DatasetFileMetadataJob


dataset_file_metadata_queue = DatasetsFileMetadataQueue(
    tasks={
        "generate_file_sample": generate_dataset_file_sample_task,
    },
    notify_channel="dataset_file_metadata_queue",
)


def load_file_metadata(file_id: str):
    dataset_file_metadata_queue.enqueue(
        {
            "generate_file_metadata",
            {
                "file_id": str(file_id),
            },
        }
    )
