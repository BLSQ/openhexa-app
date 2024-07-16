import json
from logging import getLogger

import pandas as pd
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError
from dpq.queue import AtLeastOnceQueue

from hexa.datasets.api import generate_download_url
from hexa.datasets.models import (
    DatasetFileMetadata,
    DatasetFileMetadataJob,
    DatasetVersionFile,
)
from hexa.files.api import get_storage

logger = getLogger(__name__)


def download_file_as_dataframe(dataset_version_file: DatasetVersionFile) -> dict:
    filename = dataset_version_file.filename
    file_format = filename.split(".")[-1]
    try:
        download_url = generate_download_url(dataset_version_file)
        sample = None
        if file_format == "csv":
            sample = pd.read_csv(download_url)
        elif file_format == "parquet":
            sample = pd.read_parquet(download_url)
        elif file_format == "xlsx":
            sample = pd.read_excel(download_url)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
        return {"success": True, "data": sample}

    except pd.errors.ParserError as e:
        logger.error(f"Error parsing the file {filename} content: {e}")
        return {"success": False, "errors": [f"FILE_PARSING_ERROR: {str(e)}"]}
    except ValueError as e:
        logger.error(f"Cannot read file {filename}: {e}")
        return {"success": False, "errors": [f"FILE_NOT_SUPPORTED : {str(e)}"]}
    except get_storage().exceptions.NotFound:
        logger.error(f"Cannot find file {filename}")
        return {"success": False, "errors": ["FILE_NOT_FOUND"]}


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

    logger.info(f"Creating dataset sample for version file {dataset_version_file_id}")
    try:
        dataset_file_metadata = DatasetFileMetadata.objects.create(
            dataset_version_file=dataset_version_file,
            status=DatasetFileMetadata.STATUS_PROCESSING,
        )
    except (IntegrityError, DatabaseError, ValidationError) as e:
        logger.error(f"Error creating DatasetFileMetadata: {e}")
        return

    try:
        source_file = download_file_as_dataframe(dataset_version_file)
        if source_file["success"]:
            file_content = source_file["data"]
            if not file_content.empty:
                file_sample = file_content.sample(
                    settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE,
                    random_state=22,
                    replace=True,
                )
                dataset_file_metadata.sample = file_sample.to_json(orient="records")
            else:
                dataset_file_metadata.sample = json.dumps([])
            logger.info(f"Dataset sample saved for file {dataset_version_file_id}")
            dataset_file_metadata.status = DatasetFileMetadata.STATUS_FINISHED
            dataset_file_metadata.save()
            logger.info(f"Dataset sample created for file {dataset_version_file_id}")
        else:
            dataset_file_metadata.status = DatasetFileMetadata.STATUS_FAILED
            dataset_file_metadata.status_reason = str(source_file["errors"])
            dataset_file_metadata.save()
            logger.info(
                f'Dataset file sample creation failed for file {dataset_version_file_id} with error {source_file["errors"]}'
            )
    except Exception as e:
        dataset_file_metadata.status = DatasetFileMetadata.STATUS_FAILED
        dataset_file_metadata.status_reason = str(e)
        try:
            dataset_file_metadata.save()
        except (IntegrityError, DatabaseError, ValidationError) as save_error:
            logger.error(
                f"Error saving DatasetFileMetadata after failure: {save_error}"
            )
        logger.exception(
            f"Dataset file sample creation failed for file {dataset_version_file_id}: {e}"
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
