from logging import getLogger

import pandas as pd
from django.conf import settings
from dpq.queue import AtLeastOnceQueue

from hexa.core import mimetypes
from hexa.datasets.api import generate_download_url
from hexa.datasets.models import (
    DatasetFileMetadataJob,
    DatasetFileSample,
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
        # low_memory is set to False for datatype guessing
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
    else:
        raise ValueError(f"Unsupported file format: {dataset_version_file.filename}")


def generate_sample(
    version_file: DatasetVersionFile, previous_version_id: str | None
) -> DatasetFileSample:
    if not is_sample_supported(version_file.filename):
        raise ValueError(f"Unsupported file format: {version_file.filename}")

    logger.info(f"Creating dataset sample for version file {version_file.id}")
    dataset_file_sample = DatasetFileSample.objects.create(
        dataset_version_file=version_file,
        status=DatasetFileSample.STATUS_PROCESSING,
    )
    previous_version_file = file_from_previous_version(
        version_file.filename, previous_version_id
    )
    try:
        df = get_df(version_file)
        if df.empty is False:
            sample = df.sample(
                settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE,
                random_state=SAMPLING_SEED,
                replace=True,
            )
            dataset_file_sample.sample = sample.to_dict(orient="records")
            add_system_attributes(version_file, df, previous_version_file)
        dataset_file_sample.status = DatasetFileSample.STATUS_FINISHED
        logger.info(f"Sample saved for file {version_file.id}")
    except Exception as e:
        logger.exception(f"Sample creation failed for file {version_file.id}: {e}")
        dataset_file_sample.status = DatasetFileSample.STATUS_FAILED
        dataset_file_sample.status_reason = str(e)
    finally:
        dataset_file_sample.save()
        return dataset_file_sample


def dataframe_to_sample(data: pd.DataFrame):
    random_seed = 22
    return data.sample(
        settings.WORKSPACE_DATASETS_FILE_SNAPSHOT_SIZE,
        random_state=random_seed,
        replace=True,
    )


def calculate_profiling_per_column(dataframe: pd.DataFrame) -> list:
    logger.info("Calculating profiling per column")
    for col in dataframe.select_dtypes(include=["object"]).columns:
        dataframe[col] = dataframe[col].astype("string")

    data_types = dataframe.dtypes.apply(str).to_dict()
    missing_values = dataframe.isnull().sum().to_dict()
    unique_values = dataframe.nunique().to_dict()
    distinct_values = dataframe.apply(lambda x: x.nunique(dropna=False)).to_dict()
    constant_values = (
        dataframe.apply(lambda x: x.nunique() == 1).astype("bool").to_dict()
    )

    metadata_per_column = [
        {
            "column_name": column,
            "data_type": data_types.get(column),
            "missing_values": missing_values.get(column),
            "unique_values": unique_values.get(column),
            "distinct_values": distinct_values.get(column),
            "constant_values": constant_values.get(column),
        }
        for column in dataframe.columns
    ]

    return metadata_per_column


def file_from_previous_version(
    filename: str, dataset_previous_version_id: str | None
) -> DatasetVersionFile | None:
    if dataset_previous_version_id is None or dataset_previous_version_id == "None":
        return None
    all_previous_files = DatasetVersionFile.objects.filter(
        dataset_version=dataset_previous_version_id
    ).all()
    for file in all_previous_files:
        if file.filename == filename:
            return file
    return None


def add_system_attributes(
    version_file: DatasetVersionFile,
    file_content: pd.DataFrame,
    previous_version_file: DatasetVersionFile,
):
    # Attributes from previous version file are copied to the new version file
    if previous_version_file:
        logger.info(
            f"Copying attributes from previous version - {previous_version_file}"
        )
        user_attributes = previous_version_file.get_attributes(system=False).all()
        for attribute in user_attributes:
            version_file.add_attribute(
                key=attribute.key, value=attribute.value, system=False
            )

    # Add attributes from automated profiling
    profiling = calculate_profiling_per_column(file_content)
    for profile in profiling:
        for key, value in profile.items():
            version_file.update_attribute(
                key=f'{profile["column_name"]}.{key}',
                value=value,
                system=True,
            )
        # Add description field to each column
        version_file.update_attribute(
            key=f'{profile["column_name"]}.description',
            value="Add description here",
            system=True,
        )


class DatasetsFileMetadataQueue(AtLeastOnceQueue):
    job_model = DatasetFileMetadataJob


dataset_file_metadata_queue = DatasetsFileMetadataQueue(
    tasks={
        "generate_file_metadata": lambda _, job: generate_sample(
            DatasetVersionFile.objects.get(id=job.args["file_id"]),
            job.args["previous_version_id"],
        ),
    },
    notify_channel="dataset_file_metadata_queue",
)
