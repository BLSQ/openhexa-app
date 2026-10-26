# Malaria Surveillance Workspace

Shared workspace of the national malaria programme data team. It holds the raw
extracts, the reference files and the helpers our pipelines are built from.

## Layout

| Path | What it holds |
|---|---|
| `data/raw/` | Raw extracts, one file per source system. Never edited by hand. |
| `data/boundaries/` | Administrative boundaries, refreshed once a year. |
| `data/mapping.csv` | Data element mapping between the source and target DHIS2 instances. |
| `config/` | Reference configuration shared by several pipelines. |
| `scripts/utils/` | Shared helpers. Reuse them in new pipelines instead of re-implementing them. |
| `scripts/climate/` | Helpers for the climate (ERA5) extractions. |
| `pipelines/` | Older pipelines kept for reference while they are migrated. |

## Conventions

- Connections are always referenced by slug (`dhis2-play`, `dhis2-target`,
  `iaso-staging`, `cds-climate`), never by URL or credentials.
- Pipelines write their outputs under `pipelines/<pipeline name>/output/`, and
  publish a new dataset version when the output is meant for other teams.
- Periods use the DHIS2 ISO format (`202401`, `2024Q1`, `2024`).
- Dates in file names use `YYYY-MM-DD`.
- Parquet is preferred over CSV for anything over a few thousand rows.

## Shared helpers

- `scripts/utils/dhis2_helpers.py`: period ranges, chunked data value extraction,
  org unit hierarchy flattening, data element mapping.
- `scripts/utils/io_helpers.py`: output paths, parquet/CSV writers, dataset
  publication.
- `scripts/climate/era5_utils.py`: ERA5 request building, bounding boxes from
  boundaries, daily-to-weekly aggregation.

## Contacts

Data engineering questions go to the platform channel. Questions about the
mapping file go to the HMIS focal point.
