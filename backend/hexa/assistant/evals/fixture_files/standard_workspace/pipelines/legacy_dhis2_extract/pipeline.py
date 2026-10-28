"""Legacy monthly DHIS2 extraction, kept for reference while it is migrated.

Extracts the routine malaria data elements for every facility of the source
instance and writes one parquet file per run. Superseded by pipelines built on
scripts/utils/dhis2_helpers.py.
"""

import polars as pl
from openhexa.sdk import current_run, parameter, pipeline, workspace
from openhexa.toolbox.dhis2 import DHIS2

MALARIA_DATASET = "BfMAe6Itzgt"
FACILITY_LEVEL = 4


@pipeline("legacy-dhis2-extract")
@parameter("start_period", type=str, default="202401", help="First month, YYYYMM")
@parameter("end_period", type=str, default="202412", help="Last month, YYYYMM")
def legacy_dhis2_extract(start_period: str, end_period: str):
    dhis = connect()
    org_units = facilities(dhis)
    values = extract(dhis, org_units, start_period, end_period)
    write(values)


@legacy_dhis2_extract.task
def connect() -> DHIS2:
    return DHIS2(workspace.dhis2_connection("dhis2-play"), cache_dir=".cache")


@legacy_dhis2_extract.task
def facilities(dhis: DHIS2) -> list[str]:
    org_units = dhis.meta.organisation_units()
    ids = [ou["id"] for ou in org_units if ou.get("level") == FACILITY_LEVEL]
    current_run.log_info(f"{len(ids)} facilities")
    return ids


@legacy_dhis2_extract.task
def extract(
    dhis: DHIS2, org_units: list[str], start_period: str, end_period: str
) -> pl.DataFrame:
    periods = []
    year, month = int(start_period[:4]), int(start_period[4:])
    while f"{year}{month:02d}" <= end_period:
        periods.append(f"{year}{month:02d}")
        month += 1
        if month > 12:
            year, month = year + 1, 1

    frames = []
    for i in range(0, len(org_units), 50):
        values = dhis.data_value_sets.get(
            datasets=[MALARIA_DATASET],
            periods=periods,
            org_units=org_units[i : i + 50],
        )
        if values:
            frames.append(pl.DataFrame(values))
    if not frames:
        current_run.log_warning("No data values returned")
        return pl.DataFrame()
    return pl.concat(frames, how="diagonal")


@legacy_dhis2_extract.task
def write(values: pl.DataFrame):
    path = f"{workspace.files_path}/pipelines/legacy_dhis2_extract/output/data_values.parquet"
    values.write_parquet(path)
    current_run.add_file_output(path)


if __name__ == "__main__":
    legacy_dhis2_extract()
