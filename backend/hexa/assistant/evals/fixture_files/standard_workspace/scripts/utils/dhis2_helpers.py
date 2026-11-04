"""Shared DHIS2 helpers for the workspace pipelines.

Every pipeline that talks to DHIS2 should go through these helpers rather than
calling the API directly, so that chunking, retries and period handling stay
consistent across extractions.
"""

from __future__ import annotations

import csv
import logging
import time
from collections.abc import Iterable, Iterator
from datetime import date

import polars as pl
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = ".cache"
DEFAULT_CHUNK_SIZE = 50
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

MONTHLY = "monthly"
QUARTERLY = "quarterly"
YEARLY = "yearly"


def get_client(connection_slug: str, use_cache: bool = True) -> DHIS2:
    """Build a DHIS2 client from a workspace connection slug.

    The metadata cache is shared between runs, which makes repeated
    extractions on large instances much faster.
    """
    connection = workspace.dhis2_connection(connection_slug)
    if use_cache:
        return DHIS2(connection, cache_dir=DEFAULT_CACHE_DIR)
    return DHIS2(connection)


def monthly_periods(start: str, end: str) -> list[str]:
    """Monthly DHIS2 periods between two periods, inclusive.

    >>> monthly_periods("202311", "202402")
    ['202311', '202312', '202401', '202402']
    """
    year, month = int(start[:4]), int(start[4:6])
    end_year, end_month = int(end[:4]), int(end[4:6])
    periods = []
    while (year, month) <= (end_year, end_month):
        periods.append(f"{year}{month:02d}")
        month += 1
        if month > 12:
            year, month = year + 1, 1
    return periods


def quarterly_periods(start: str, end: str) -> list[str]:
    """Quarterly DHIS2 periods between two periods, inclusive.

    >>> quarterly_periods("2023Q3", "2024Q2")
    ['2023Q3', '2023Q4', '2024Q1', '2024Q2']
    """
    year, quarter = int(start[:4]), int(start[5])
    end_year, end_quarter = int(end[:4]), int(end[5])
    periods = []
    while (year, quarter) <= (end_year, end_quarter):
        periods.append(f"{year}Q{quarter}")
        quarter += 1
        if quarter > 4:
            year, quarter = year + 1, 1
    return periods


def yearly_periods(start: str, end: str) -> list[str]:
    return [str(year) for year in range(int(start), int(end) + 1)]


def period_range(start: str, end: str, frequency: str = MONTHLY) -> list[str]:
    """Periods between start and end for the given frequency."""
    if frequency == MONTHLY:
        return monthly_periods(start, end)
    if frequency == QUARTERLY:
        return quarterly_periods(start, end)
    if frequency == YEARLY:
        return yearly_periods(start, end)
    raise ValueError(f"Unknown frequency: {frequency}")


def last_complete_month(today: date | None = None) -> str:
    """The most recent month whose reporting deadline has passed."""
    today = today or date.today()
    year, month = today.year, today.month - 1
    if month == 0:
        year, month = year - 1, 12
    return f"{year}{month:02d}"


def chunks(items: list, size: int = DEFAULT_CHUNK_SIZE) -> Iterator[list]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _with_retries(func, *args, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            if attempt == MAX_RETRIES:
                raise
            logger.warning("Attempt %s failed (%s), retrying", attempt, exc)
            time.sleep(RETRY_DELAY_SECONDS * attempt)
    return None


def org_units_at_level(dhis: DHIS2, level: int) -> list[dict]:
    """Organisation units of one hierarchy level."""
    org_units = dhis.meta.organisation_units()
    return [ou for ou in org_units if ou.get("level") == level]


def org_unit_ids(
    dhis: DHIS2, level: int | None = None, parent: str | None = None
) -> list[str]:
    """Identifiers of the org units at a level, optionally under a parent."""
    org_units = dhis.meta.organisation_units()
    selected = []
    for ou in org_units:
        if level is not None and ou.get("level") != level:
            continue
        if parent is not None and f"/{parent}/" not in f"{ou.get('path', '')}/":
            continue
        selected.append(ou["id"])
    return selected


def flatten_hierarchy(org_units: list[dict], max_level: int = 5) -> pl.DataFrame:
    """One row per org unit with its ancestors as level_N_id / level_N_name columns."""
    names = {ou["id"]: ou.get("name") for ou in org_units}
    rows = []
    for ou in org_units:
        ancestors = [part for part in ou.get("path", "").split("/") if part]
        row = {"id": ou["id"], "name": ou.get("name"), "level": ou.get("level")}
        for lvl in range(1, max_level + 1):
            ancestor = ancestors[lvl - 1] if lvl <= len(ancestors) else None
            row[f"level_{lvl}_id"] = ancestor
            row[f"level_{lvl}_name"] = names.get(ancestor) if ancestor else None
        rows.append(row)
    return pl.DataFrame(rows)


def extract_data_values(
    dhis: DHIS2,
    org_units: list[str],
    periods: list[str],
    datasets: list[str] | None = None,
    data_elements: list[str] | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> pl.DataFrame:
    """Raw data values for org units and periods, fetched in chunks of org units.

    Large instances time out on a single request covering every facility, so
    the org units are split and the results concatenated.
    """
    if not datasets and not data_elements:
        raise ValueError("Pass datasets or data_elements")

    frames = []
    for i, org_unit_chunk in enumerate(chunks(org_units, chunk_size), start=1):
        logger.info("Extracting chunk %s (%s org units)", i, len(org_unit_chunk))
        values = _with_retries(
            dhis.data_value_sets.get,
            datasets=datasets,
            data_elements=data_elements,
            periods=periods,
            org_units=org_unit_chunk,
        )
        if values:
            frames.append(pl.DataFrame(values))
    if not frames:
        return pl.DataFrame()
    return pl.concat(frames, how="diagonal")


def load_mapping(path: str) -> dict[str, str]:
    """Read a source_de,target_de mapping CSV into a dict."""
    with open(path, newline="") as f:
        return {row["source_de"]: row["target_de"] for row in csv.DictReader(f)}


def apply_mapping(values: pl.DataFrame, mapping: dict[str, str]) -> pl.DataFrame:
    """Rename data elements using a mapping, dropping the unmapped ones."""
    unmapped = set(values["dataElement"].unique()) - set(mapping)
    if unmapped:
        logger.warning(
            "%s data elements have no mapping and are dropped", len(unmapped)
        )
    return values.filter(pl.col("dataElement").is_in(list(mapping))).with_columns(
        pl.col("dataElement").replace(mapping)
    )


def to_import_payload(values: pl.DataFrame) -> list[dict]:
    """Shape data values as the dataValues list DHIS2 expects on import."""
    columns = ["dataElement", "period", "orgUnit", "categoryOptionCombo", "value"]
    return values.select([c for c in columns if c in values.columns]).to_dicts()


def summarize(
    values: pl.DataFrame, by: Iterable[str] = ("dataElement", "period")
) -> pl.DataFrame:
    """Count of values per group, used in run logs to spot empty extractions."""
    return values.group_by(list(by)).len().sort(list(by))
