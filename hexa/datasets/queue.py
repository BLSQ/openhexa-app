from logging import getLogger

import pandas as pd
from django.conf import settings
from dpq.queue import AtLeastOnceQueue

from hexa.datasets.api import generate_download_url
from hexa.datasets.models import (
    DatasetFileMetadata,
    DatasetFileMetadataJob,
    DatasetVersionFile,
)

logger = getLogger(__name__)


def download_file_sample(dataset_version_file: DatasetVersionFile) -> pd.DataFrame:
    filename = dataset_version_file.filename
    file_format = filename.split(".")[-1]
    try:
        download_url = generate_download_url(dataset_version_file)
        if file_format == "csv":
            return pd.read_csv(download_url)
        elif file_format == "parquet":
            return pd.read_parquet(download_url, engine="pyarrow")
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    except pd.errors.ParserError as e:
        print(f"Error parsing the file content: {e}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"Cannot read file: {e}")
        return pd.DataFrame()


def generate_dataset_file_sample_task(
    queue: AtLeastOnceQueue, job: DatasetFileMetadataJob
):
    dataset_version_file_id = job.args["file_id"]
    dataset_version_file = DatasetVersionFile.objects.get(id=dataset_version_file_id)
    logger.info(f"Creating dataset snapshot for version file {dataset_version_file_id}")
    dataset_file_metadata = DatasetFileMetadata.objects.create(
        dataset_version_file=dataset_version_file,
        status=DatasetFileMetadata.STATUS_PROCESSING,
    )

    try:
        file_snapshot_df = download_file_sample(dataset_version_file)
        if not file_snapshot_df.empty:
            file_snapshot_content = file_snapshot_df.head(
                settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE
            )
            dataset_file_metadata.sample = file_snapshot_content.to_json(
                orient="records"
            )
            logger.info(f"Dataset snapshot saved for file {dataset_version_file_id}")
        else:
            logger.info(f"Dataset snapshot is empty for file {dataset_version_file_id}")
        dataset_file_metadata.status = DatasetFileMetadata.STATUS_FINISHED
        dataset_file_metadata.save()
        logger.info("Dataset snapshot created for file {dataset_version_file_id}")
    except Exception as e:
        print(f"Fail : {e}")
        dataset_file_metadata.status = DatasetFileMetadata.STATUS_FAILED
        dataset_file_metadata.save()
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
