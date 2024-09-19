from logging import getLogger

import pandas as pd
from django.conf import settings
from dpq.queue import AtLeastOnceQueue

from hexa.core import mimetypes
from hexa.datasets.api import generate_download_url
from hexa.datasets.models import (
    DatasetFileMetadata,
    DatasetFileMetadataJob,
    DatasetVersionFile,
)

logger = getLogger(__name__)

SAMPLING_SEED = 22


def is_sample_supported(filename: str) -> bool:
    supported_mimetypes = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/vnd.apache.parquet",
        "text/csv",
    ]
    supported_extensions = ["parquet"]
    suffix = filename.split(".")[-1]
    mime_type, _ = mimetypes.guess_type(filename, strict=False)
    return mime_type in supported_mimetypes or suffix in supported_extensions


def get_df(dataset_version_file: DatasetVersionFile) -> pd.DataFrame:
    mime_type, _ = mimetypes.guess_type(dataset_version_file.filename, strict=False)
    try:
        download_url = generate_download_url(
            dataset_version_file, host=settings.INTERNAL_BASE_URL
        )
    except Exception as e:
        logger.error(e)
        raise e

    if mime_type == "text/csv":
        return pd.read_csv(download_url)
    elif (
        mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        or mime_type == "application/vnd.ms-excel"
    ):
        return pd.read_excel(download_url)
    elif (
        mime_type == "application/vnd.apache.parquet"
        or dataset_version_file.filename.split(".")[-1] == "parquet"
    ):
        return pd.read_parquet(download_url)
    else:
        raise ValueError(f"Unsupported file format: {dataset_version_file.filename}")


def generate_sample(version_file: DatasetVersionFile) -> DatasetFileMetadata:
    if not is_sample_supported(version_file.filename):
        raise ValueError(f"Unsupported file format: {version_file.filename}")

    logger.info(f"Creating dataset sample for version file {version_file.id}")
    dataset_file_metadata = DatasetFileMetadata.objects.create(
        dataset_version_file=version_file,
        status=DatasetFileMetadata.STATUS_PROCESSING,
    )

    try:
        df = get_df(version_file)
        if df.empty is False:
            sample = df.sample(
                settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE,
                random_state=SAMPLING_SEED,
                replace=True,
            )
            dataset_file_metadata.sample = sample.to_dict(orient="records")
        dataset_file_metadata.status = DatasetFileMetadata.STATUS_FINISHED
        logger.info(f"Sample saved for file {version_file.id}")
    except Exception as e:
        logger.exception(f"Sample creation failed for file {version_file.id}: {e}")
        dataset_file_metadata.status = DatasetFileMetadata.STATUS_FAILED
        dataset_file_metadata.status_reason = str(e)
    finally:
        dataset_file_metadata.save()
        return dataset_file_metadata


class DatasetsFileMetadataQueue(AtLeastOnceQueue):
    job_model = DatasetFileMetadataJob


dataset_file_metadata_queue = DatasetsFileMetadataQueue(
    tasks={
        "generate_file_metadata": lambda _, job: generate_sample(
            DatasetVersionFile.objects.get(id=job.args["file_id"])
        ),
    },
    notify_channel="dataset_file_metadata_queue",
)
