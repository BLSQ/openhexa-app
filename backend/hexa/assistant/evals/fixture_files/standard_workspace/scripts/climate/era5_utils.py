"""Helpers for the ERA5 climate extractions from the Copernicus Climate Data Store."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta

import polars as pl
from openhexa.sdk import workspace

logger = logging.getLogger(__name__)

CDS_CONNECTION_SLUG = "cds-climate"
DATASET_NAME = "reanalysis-era5-land"

VARIABLES = {
    "total_precipitation": "tp",
    "2m_temperature": "t2m",
    "2m_dewpoint_temperature": "d2m",
}

# Padding added around the boundaries so border cells are not cut off.
BBOX_PADDING_DEGREES = 0.1


@dataclass(frozen=True)
class BoundingBox:
    north: float
    west: float
    south: float
    east: float

    def as_area(self) -> list[float]:
        """The [N, W, S, E] order the CDS API expects."""
        return [self.north, self.west, self.south, self.east]

    def padded(self, degrees: float = BBOX_PADDING_DEGREES) -> BoundingBox:
        return BoundingBox(
            north=self.north + degrees,
            west=self.west - degrees,
            south=self.south - degrees,
            east=self.east + degrees,
        )


def cds_credentials() -> tuple[str, str]:
    """URL and key of the CDS custom connection."""
    connection = workspace.custom_connection(CDS_CONNECTION_SLUG)
    return connection.url, connection.key


def bbox_from_boundaries(boundaries: pl.DataFrame) -> BoundingBox:
    """Bounding box of a boundaries table with min/max lon/lat columns."""
    return BoundingBox(
        north=boundaries["max_lat"].max(),
        west=boundaries["min_lon"].min(),
        south=boundaries["min_lat"].min(),
        east=boundaries["max_lon"].max(),
    ).padded()


def days_between(start: date, end: date) -> list[date]:
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def build_request(variable: str, year: int, month: int, bbox: BoundingBox) -> dict:
    """One CDS request: a variable over one month, hourly, cropped to the bbox."""
    if variable not in VARIABLES:
        raise ValueError(
            f"Unsupported variable {variable}; choose from {sorted(VARIABLES)}"
        )
    return {
        "variable": [variable],
        "year": str(year),
        "month": f"{month:02d}",
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "area": bbox.as_area(),
        "data_format": "netcdf",
    }


def months_between(start: date, end: date) -> list[tuple[int, int]]:
    months = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        months.append((year, month))
        month += 1
        if month > 12:
            year, month = year + 1, 1
    return months


def kelvin_to_celsius(df: pl.DataFrame, column: str) -> pl.DataFrame:
    return df.with_columns((pl.col(column) - 273.15).alias(column))


def metres_to_millimetres(df: pl.DataFrame, column: str) -> pl.DataFrame:
    return df.with_columns((pl.col(column) * 1000).alias(column))


def daily_to_epi_weeks(
    daily: pl.DataFrame, value: str, how: str = "mean"
) -> pl.DataFrame:
    """Aggregate a daily series per org unit to ISO weeks, as used by the epi team.

    Precipitation is summed over the week, temperatures are averaged.
    """
    agg = pl.col(value).sum() if how == "sum" else pl.col(value).mean()
    return (
        daily.with_columns(
            pl.col("date").dt.iso_year().alias("year"),
            pl.col("date").dt.week().alias("week"),
        )
        .group_by(["org_unit_id", "year", "week"])
        .agg(agg.alias(value))
        .with_columns(
            pl.format("{}W{}", pl.col("year"), pl.col("week")).alias("period")
        )
        .sort(["org_unit_id", "year", "week"])
    )
