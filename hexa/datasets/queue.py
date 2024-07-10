import os.path
from logging import getLogger

from dpq.queue import AtLeastOnceQueue

from hexa.datasets.models import DatasetFileMetadataJob
from hexa.datasets.models import (
    DatasetFileSnapshot,
    DatasetVersionFile,
)
from hexa.files.api import get_storage
from hexa.user_management.models import User

logger = getLogger(__name__)

# qdd to settings
DEFAULT_SNAPSHOT_LINES = 50


def generate_dataset_file_sample_task(queue: AtLeastOnceQueue, job: DatasetSnapshotJob):
    try:
        dataset_version_file_id = job.args["file_id"]
        user_id = job.args["user_id"]
        logger.info(
            f"Creating dataset snapshot for version file {dataset_version_file_id}"
        )
        dataset_version_file = DatasetVersionFile.objects.get(
            id=dataset_version_file_id
        )
        user = User.objects.get(id=user_id)

        storage = get_storage()
        dataset_snapshot = storage.read_object_lines(
            dataset_version_file, DEFAULT_SNAPSHOT_LINES
        )
        bucket_name = dataset_version_file.uri.split("/")[0]
        filename, extension = os.path.splitext(dataset_version_file.uri)
        upload_uri = f"{filename}-snapshot{extension}"
        storage.upload_object_from_string(bucket_name, upload_uri, dataset_snapshot)

        logger.info(
            f"Uploaded dataset snapshot to {upload_uri} for file {dataset_version_file_id}"
        )
        DatasetFileSnapshot.objects.create_if_has_perm(
            principal=user, dataset_version_file=dataset_version_file, uri=upload_uri
        )
        logger.info("Dataset snapshot created for file {dataset_version_file_id}")
    except Exception as e:
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
