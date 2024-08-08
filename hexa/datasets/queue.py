import json
from logging import getLogger

import pandas as pd
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError
from dpq.queue import AtLeastOnceQueue

from hexa.core import mimetypes
from hexa.datasets.api import generate_download_url
from hexa.datasets.models import (
    DatasetFileMetadata,
    DatasetFileMetadataJob,
    DatasetVersionFile,
)

logger = getLogger(__name__)


def is_supported_mimetype(filename: str) -> bool:
    supported_mimetypes = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/vnd.apache.parquet",
        "text/csv",
    ]
    supported_extensions = ["parquet"]
    suffix = filename.split(".")[-1]
    mime_type, encoding = mimetypes.guess_type(filename, strict=False)
    return mime_type in supported_mimetypes or suffix in supported_extensions


def download_file_as_dataframe(
    dataset_version_file: DatasetVersionFile,
) -> pd.DataFrame | None:
    mime_type, encoding = mimetypes.guess_type(
        dataset_version_file.filename, strict=False
    )
    download_url = generate_download_url(dataset_version_file)
    if mime_type == "text/csv":
        return pd.read_csv(download_url, low_memory=False)
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


def metadata_profiling(file_content: pd.DataFrame) -> list:
    for col in file_content.select_dtypes(include=["object"]).columns:
        file_content[col] = file_content[col].astype("string")

    data_types = file_content.dtypes.apply(str).to_dict()
    missing_values = file_content.isnull().sum().to_dict()
    unique_values = file_content.nunique().to_dict()
    distinct_values = file_content.apply(lambda x: x.nunique(dropna=False)).to_dict()
    constant_values = (
        file_content.apply(lambda x: x.nunique() == 1).astype("bool").to_dict()
    )

    metadata_per_column = [
        {
            "column_names": column,
            "data_types": data_types.get(column, "-"),
            "missing_values": missing_values.get(column, "-"),
            "unique_values": unique_values.get(column, "-"),
            "distinct_values": distinct_values.get(column, "-"),
            "constant_values": constant_values.get(column, "-"),
        }
        for column in file_content.columns
    ]

    return metadata_per_column


def generate_dataset_file_sample_task(
    queue: AtLeastOnceQueue, job: DatasetFileMetadataJob
):
    dataset_version_file_id = job.args["file_id"]
    try:
        dataset_version_file = DatasetVersionFile.objects.get(
            id=dataset_version_file_id
        )
    except ObjectDoesNotExist as e:
        logger.error(
            f"DatasetVersionFile with id {dataset_version_file_id} does not exist: {e}"
        )
        return

    if not is_supported_mimetype(dataset_version_file.filename):
        logger.info(f"Unsupported file format: {dataset_version_file.filename}")
        return

    logger.info(f"Creating dataset sample for version file {dataset_version_file.id}")
    try:
        dataset_file_metadata = DatasetFileMetadata.objects.create(
            dataset_version_file=dataset_version_file,
            status=DatasetFileMetadata.STATUS_PROCESSING,
        )
    except (IntegrityError, DatabaseError, ValidationError) as e:
        logger.error(f"Error creating DatasetFileMetadata: {e}")
        return

    try:
        file_content = download_file_as_dataframe(dataset_version_file)
        if not file_content.empty:
            random_seed = 22
            file_sample = file_content.sample(
                settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE,
                random_state=random_seed,
                replace=True,
            )
            dataset_file_metadata.sample = file_sample.to_json(orient="records")
            dataset_file_metadata.profiling = json.dumps(
                metadata_profiling(file_content)
            )
        else:
            dataset_file_metadata.sample = json.dumps([])
        logger.info(f"Dataset sample saved for file {dataset_version_file_id}")
        dataset_file_metadata.status = DatasetFileMetadata.STATUS_FINISHED
        dataset_file_metadata.save()
        logger.info(f"Dataset sample created for file {dataset_version_file_id}")
    except Exception as e:
        dataset_file_metadata.status = DatasetFileMetadata.STATUS_FAILED
        dataset_file_metadata.status_reason = str(e)
        dataset_file_metadata.save()
        logger.exception(
            f"Dataset file sample creation failed for file {dataset_version_file_id}: {e}"
        )


class DatasetsFileMetadataQueue(AtLeastOnceQueue):
    job_model = DatasetFileMetadataJob


dataset_file_metadata_queue = DatasetsFileMetadataQueue(
    tasks={
        "generate_file_metadata": generate_dataset_file_sample_task,
    },
    notify_channel="dataset_file_metadata_queue",
)


def load_file_metadata(file_id: str):
    dataset_file_metadata_queue.enqueue(
        "generate_file_metadata",
        {
            "file_id": str(file_id),
        },
    )
