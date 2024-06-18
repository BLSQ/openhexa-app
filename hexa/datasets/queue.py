from logging import getLogger

from dpq.queue import AtLeastOnceQueue

from hexa.datasets.models import DatasetSnapshotJob

logger = getLogger(__name__)


def create_dataset_snnapshot_task(queue: AtLeastOnceQueue, job: DatasetSnapshotJob):
    # TODO: imlpement ticket PATHWAYS-98  - extract data in background task
    dataset_version_file_id = job.args["fileId"]
    logger.info(f"Creating dataset version file {dataset_version_file_id}")


class DatasetSnapshotQueue(AtLeastOnceQueue):
    job_model = DatasetSnapshotJob


dataset_snapshot_queue = DatasetSnapshotQueue(
    tasks={
        "create_snapshot": create_dataset_snnapshot_task,
    },
    notify_channel="dataset_snapshot_queue",
)
