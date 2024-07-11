from logging import getLogger

import pandas as pd
from django.conf import settings
from dpq.queue import AtLeastOnceQueue

from hexa.datasets.api import generate_download_url
from hexa.datasets.models import DatasetFileMetadataJob
from hexa.datasets.models import (
    DatasetFileSnapshot,
    DatasetVersionFile,
)
from hexa.files.api import get_storage

logger = getLogger(__name__)


def read_file_content(download_url: str, content_type: str) -> pd.DataFrame:
    try:
        if content_type == "text/csv":
            return pd.read_csv(download_url)
        elif content_type == "application/octet-stream":
            return pd.read_parquet(download_url)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    except pd.errors.ParserError as e:
        print(f"Error parsing the file content: {e}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"Unsupported file content: {e}")
        return pd.DataFrame()


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

        download_url = generate_download_url(dataset_version_file)
        file_snapshot_df = read_file_content(
            download_url, dataset_version_file.content_type
        )
        if not file_snapshot_df.empty:
            file_snapshot_content = file_snapshot_df.head(
                settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE
            )
            dataset_file_snapshot.content = file_snapshot_content.to_json(
                orient="records"
            )
            logger.info(f"Dataset snapshot saved for file {dataset_version_file_id}")
        else:
            logger.info(f"Dataset snapshot is empty for file {dataset_version_file_id}")
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
        logger.exception(
            f"Dataset file snapshot creation failed for file {dataset_version_file_id}: {e}"
        )


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
