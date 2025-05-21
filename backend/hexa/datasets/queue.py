import hashlib
from logging import getLogger
from typing import Type

import numpy as np
import pandas as pd
from django.conf import settings
from django.db import transaction
from dpq.queue import AtMostOnceQueue, Queue

from hexa.core import mimetypes
from hexa.datasets.api import generate_download_url
from hexa.datasets.models import (
    BaseJobWithRetry,
    DatasetFileMetadataJob,
    DatasetFileSample,
    DatasetVersion,
    DatasetVersionFile,
)

logger = getLogger(__name__)

# Used for reproducibility for the sample extraction
SAMPLING_SEED = 22


def is_file_supported(filename: str) -> bool:
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


def load_df(dataset_version_file: DatasetVersionFile) -> pd.DataFrame:
    mime_type, _ = mimetypes.guess_type(dataset_version_file.filename, strict=False)
    try:
        logger.info(f"Using {settings.INTERNAL_BASE_URL}")
        download_url = generate_download_url(
            dataset_version_file, host=settings.INTERNAL_BASE_URL
        )
    except Exception as e:
        logger.exception("Unable to generate a download url", exc_info=e)
        raise

    if mime_type == "text/csv":
        # low_memory is set to False for datatype guessing
        return pd.read_csv(download_url, low_memory=False)
    elif (
        mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        or mime_type == "application/vnd.ms-excel"
    ):
        return pd.read_excel(download_url, engine="openpyxl")
    elif (
        mime_type == "application/vnd.apache.parquet"
        or dataset_version_file.filename.split(".")[-1] == "parquet"
    ):
        return pd.read_parquet(download_url)
    else:
        raise ValueError(f"Unsupported file format: {dataset_version_file.filename}")


def generate_sample(
    version_file: DatasetVersionFile, df: pd.DataFrame
) -> DatasetFileSample:
    logger.info(f"Creating dataset sample for version file {version_file.id}")
    dataset_file_sample = DatasetFileSample.objects.create(
        dataset_version_file=version_file,
        status=DatasetFileSample.STATUS_PROCESSING,
    )
    try:
        if df.empty is False:
            sample = df.sample(
                settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE,
                random_state=SAMPLING_SEED,
                replace=True,
            )
            sample = sample.replace(
                [np.inf, -np.inf], np.nan
            )  # We are not supporting Infinity
            dataset_file_sample.sample = sample.to_dict(orient="records")
        dataset_file_sample.status = DatasetFileSample.STATUS_FINISHED
    except Exception as e:
        logger.exception(
            f"Sample creation failed for file {version_file.id}: {e}", exc_info=e
        )
        dataset_file_sample.status = DatasetFileSample.STATUS_FAILED
        dataset_file_sample.status_reason = str(e)

    try:
        dataset_file_sample.save()
    except Exception as e:
        logger.exception(
            f"Sample creation failed for file {version_file.id}: {e}", exc_info=e
        )
    finally:
        return dataset_file_sample


def generate_profile(df: pd.DataFrame) -> list:
    logger.info("Starting profiling calculation per column")
    try:
        for col in df.select_dtypes(include=["object"]).columns:
            try:
                df[col] = df[col].astype("string")
            except Exception as e:
                logger.warning(f"Failed to convert column '{col}' to string: {e}")
                df.drop(columns=[col], inplace=True)

        data_types = df.dtypes.apply(str).to_dict()
        missing_values = df.isnull().sum().to_dict()
        unique_values = df.nunique().to_dict()
        distinct_values = df.apply(lambda x: x.nunique(dropna=False)).to_dict()
        constant_values = df.apply(lambda x: x.nunique() == 1).astype("bool").to_dict()
        count = df.count().to_dict()

        numeric_df = df.select_dtypes(include=["number"]).replace(
            [np.inf, -np.inf], np.nan
        )
        numeric_df = numeric_df.dropna(
            how="all", axis=1
        )  # Drop numeric columns with all NaN values

        mean = numeric_df.mean().to_dict()
        minimum = numeric_df.min().to_dict()
        maximum = numeric_df.max().to_dict()
        quantiles25 = numeric_df.quantile(0.25).to_dict()
        median = numeric_df.median().to_dict()
        quantiles75 = numeric_df.quantile(0.75).to_dict()
        standard_deviation = numeric_df.std().replace({np.nan: 0.0}).to_dict()
        metadata_per_column = [
            {
                **{
                    "column_name": str(column),
                    "count": count.get(column),
                    "data_type": data_types.get(column),
                    "missing_values": missing_values.get(column),
                    "unique_values": unique_values.get(column),
                    "distinct_values": distinct_values.get(column),
                    "constant_values": constant_values.get(column),
                },
                **(
                    {
                        "mean": mean.get(column),
                        "minimum": minimum.get(column),
                        "maximum": maximum.get(column),
                        "quantiles25": quantiles25.get(column),
                        "median": median.get(column),
                        "quantiles75": quantiles75.get(column),
                        "standard_deviation": standard_deviation.get(column),
                    }
                    if column in numeric_df.columns
                    else {}
                ),
            }
            for column in df.columns
        ]
        logger.info("Finished profiling calculation per column")
        return metadata_per_column

    except Exception as e:
        logger.exception("Failed to calculate profiling", exc_info=e)
        return []


def get_previous_version_file(
    version_file: DatasetVersionFile,
) -> DatasetVersionFile | None:
    try:
        # We need to do it in two steps because we only want to get the matching file IF it's from the previous version (not any previous version)
        prev_version = (
            DatasetVersion.objects.filter(
                dataset=version_file.dataset_version.dataset,
                created_at__lt=version_file.dataset_version.created_at,
            )
            .order_by("-created_at")
            .first()
        )
        if prev_version is None:
            return None
        return (
            DatasetVersionFile.objects.filter_by_filename(version_file.filename)
            .filter(dataset_version=prev_version)
            .get()
        )
    except DatasetVersionFile.DoesNotExist:
        # The file do not exist in the previous version
        return None


def add_system_attributes(version_file: DatasetVersionFile, df: pd.DataFrame | None):
    """Add user defined attributes to the file based on the previous version and automated profiling if a dataframe has been passed."""
    # Copy user attributes from the previous version of the file if it exists
    prev_file = get_previous_version_file(version_file)
    if prev_file:
        logger.info(f"Copying attributes from previous version - {prev_file}")
        for attribute in prev_file.attributes.filter(system=False).all():
            logger.info(f"Attribute {attribute.key}={attribute.value} copied")
            version_file.update_or_create_attribute(
                key=attribute.key,
                value=attribute.value,
                label=attribute.label,
                system=False,
            )

    # Add attributes from automated profiling (if the file is supported)
    if df is None:
        return
    profiling = generate_profile(df)
    columns = {}
    for column_profile in profiling:
        for key, value in column_profile.items():
            hashed_column_name = hashlib.md5(
                column_profile["column_name"].encode()
            ).hexdigest()
            columns[hashed_column_name] = column_profile["column_name"]
            version_file.update_or_create_attribute(
                key=f"{hashed_column_name}.{key}",
                value=value,
                system=True,
            )
    version_file.properties["columns"] = columns
    version_file.save()
    # Set properties map


def generate_file_metadata_task(file_id: str) -> None:
    """Task to extract a sample of tabular files, generate profiling metadata when possible and copy user defined attributes."""
    try:
        version_file = DatasetVersionFile.objects.get(id=file_id)
    except DatasetVersionFile.DoesNotExist:
        logger.info(f"Dataset file {file_id} not found.")
        return

    logger.info("Generating metadata for file %s", version_file.id)
    df = None
    try:
        # We only support tabular data for now (CSV, Excel, Parquet) for the sample generation & profiling
        if is_file_supported(version_file.filename):
            df = load_df(version_file)
            generate_sample(version_file, df)
    except Exception as e:
        logger.exception(
            f"Failed to load dataframe for file {version_file.id}", exc_info=e
        )
        return
    logger.info("Finished sample generation, calculating profiling")
    add_system_attributes(version_file, df)


class AtMostLimitedAmountQueue(Queue):
    def __init__(self, job_model: Type[BaseJobWithRetry], *args, **kwargs):
        self.job_model = job_model
        super().__init__(*args, **kwargs)

    def run_once(self, exclude_ids=[]):
        job: BaseJobWithRetry | None = None
        try:
            with transaction.atomic():
                job = self.job_model.dequeue(exclude_ids=exclude_ids)
                if job:
                    self.logger.debug(
                        "Claimed %r.", job, extra={"data": {"job": job.to_json()}}
                    )
                    if job.retry_count < job.max_retries:
                        try:
                            result = self.run_job(job)
                            return (job, result, None)
                        except Exception as e:
                            self.handle_job_failure(job, e)
                            raise e
                    else:
                        self.logger.error(
                            f"Job {job.id} reached max retries, skipping."
                        )
                        return None
                return None
        except Exception as e:
            return (job, None, e)

    def handle_job_failure(self, job: BaseJobWithRetry, exception: Exception):
        job.retry_count += 1
        self.logger.warning(
            f"Job {job.id} failed: {exception}, retrying {job.retry_count}/{job.max_retries}"
        )
        if job.retry_count >= job.max_retries:
            self.logger.error(f"Job {job.id} failed after max retries")
        job.save()


class DatasetsFileMetadataQueue(AtMostOnceQueue):
    job_model = DatasetFileMetadataJob


dataset_file_metadata_queue = DatasetsFileMetadataQueue(
    tasks={
        "generate_file_metadata": lambda _, job: generate_file_metadata_task(
            job.args["file_id"]
        ),
    },
    notify_channel="dataset_file_metadata_queue",
)
