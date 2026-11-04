"""Shared I/O helpers: where pipelines write, and how outputs are published."""

from __future__ import annotations

import logging
import os
from datetime import date
from pathlib import Path

import polars as pl
from openhexa.sdk import current_run, workspace

logger = logging.getLogger(__name__)

PARQUET_THRESHOLD_ROWS = 5000


def output_dir(pipeline_name: str) -> Path:
    """The output directory of a pipeline, created if needed."""
    path = Path(workspace.files_path) / "pipelines" / pipeline_name / "output"
    path.mkdir(parents=True, exist_ok=True)
    return path


def dated_filename(stem: str, extension: str, day: date | None = None) -> str:
    day = day or date.today()
    return f"{stem}_{day.isoformat()}.{extension}"


def write_table(df: pl.DataFrame, pipeline_name: str, stem: str) -> Path:
    """Write a table as parquet, or CSV when it is small enough to open by hand."""
    directory = output_dir(pipeline_name)
    if df.height > PARQUET_THRESHOLD_ROWS:
        path = directory / dated_filename(stem, "parquet")
        df.write_parquet(path)
    else:
        path = directory / dated_filename(stem, "csv")
        df.write_csv(path)
    current_run.add_file_output(str(path))
    logger.info("Wrote %s rows to %s", df.height, path)
    return path


def workspace_path(relative: str) -> str:
    """Absolute path of a file given relative to the workspace root."""
    if os.path.isabs(relative):
        return relative
    return os.path.join(workspace.files_path, relative)


def read_table(relative: str) -> pl.DataFrame:
    path = workspace_path(relative)
    if path.endswith(".parquet"):
        return pl.read_parquet(path)
    if path.endswith(".csv"):
        return pl.read_csv(path)
    raise ValueError(f"Unsupported table format: {path}")


def publish_files(
    dataset_slug: str, paths: list[str], version_name: str | None = None
) -> None:
    """Publish files as a new version of an existing workspace dataset.

    Version names default to today's date, which is what the consumers of our
    datasets filter on.
    """
    dataset = workspace.get_dataset(dataset_slug)
    version = dataset.create_version(version_name or date.today().isoformat())
    for path in paths:
        version.add_file(workspace_path(path), filename=os.path.basename(path))
        current_run.log_info(f"Added {path} to {dataset_slug}")


def check_not_empty(df: pl.DataFrame, what: str) -> None:
    """Fail the run on an empty extraction rather than publish an empty file."""
    if df.is_empty():
        current_run.log_error(f"No {what} found")
        raise RuntimeError(f"No {what} found")
