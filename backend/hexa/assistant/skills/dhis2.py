from . import register_skill

DHIS2_ROUTING_SKILL = """
# DHIS2 Integration

You have access to DHIS2 connections in this workspace. You can help users with:

1. **Querying DHIS2 metadata** — organisation units, data elements, indicators, datasets, programs
2. **Querying analytics data** — aggregated data from the analytics endpoint
3. **Querying data values** — raw data values from data value sets
4. **Writing Python code** — help users write scripts using the `openhexa.toolbox.dhis2` library

## Available Tools

- `list_dhis2_connections` — List DHIS2 connections available in this workspace
- `dhis2_query_metadata` — Query metadata (org units, data elements, indicators, datasets, etc.)
- `dhis2_query_analytics` — Query aggregated analytics data
- `dhis2_query_data_values` — Query raw data values

## When to fetch detailed skill information

Use `get_skill_details` to load detailed guidance for specific DHIS2 topics:

| Sub-skill name | When to use |
|---|---|
| `dhis2-metadata` | Querying org units, data elements, indicators, datasets, programs, and other metadata |
| `dhis2-analytics` | Querying aggregated analytics data |
| `dhis2-data-values` | Querying or understanding raw data value sets |
| `dhis2-python-sdk` | Helping users write Python code with the openhexa-toolbox DHIS2 SDK |

## Important Guidelines

- Always start by listing connections with `list_dhis2_connections` to know what's available.
- When the user asks about a specific topic, fetch the relevant sub-skill details first.
- **Be efficient with tool calls**: only fetch the sub-skill details you actually need (usually just one). Don't fetch all sub-skills.
- **When writing code or notebooks**: fetch `dhis2-python-sdk` and at most 1-2 metadata queries to understand what's available, then write the code. Don't exhaustively explore all metadata types — use a few representative examples and let the user's code discover the rest.
- **Minimize metadata exploration**: query only the metadata types directly relevant to the user's request. Use `page_size=5` for exploratory queries.
"""

DHIS2_METADATA_SKILL = """
# DHIS2 Metadata Querying

Use the `dhis2_query_metadata` tool to query DHIS2 metadata.

## Parameters

- `connection_slug` (required): The slug of the DHIS2 connection to use
- `query_type` (required): One of:
  - `ORG_UNITS` — Organisation units
  - `ORG_UNIT_GROUPS` — Organisation unit groups
  - `ORG_UNIT_LEVELS` — Organisation unit levels
  - `DATASETS` — Datasets
  - `DATA_ELEMENTS` — Data elements
  - `DATA_ELEMENT_GROUPS` — Data element groups
  - `INDICATORS` — Indicators
  - `INDICATOR_GROUPS` — Indicator groups
- `fields` (optional): Comma-separated field names to include (e.g. "id,name,level")
- `filters` (optional): List of DHIS2 API filters (e.g. ["name:ilike:malaria"])
- `page` (optional): Page number for paginated results
- `page_size` (optional): Number of results per page

## Default Fields by Query Type

- `ORG_UNITS`: id, name, level, path, geometry
- `ORG_UNIT_GROUPS`: id, name, organisationUnits
- `ORG_UNIT_LEVELS`: id, name, level
- `DATASETS`: id, name, dataSetElements, indicators, organisationUnits
- `DATA_ELEMENTS`: id, name, aggregationType, zeroIsSignificant
- `DATA_ELEMENT_GROUPS`: id, name, dataElements
- `INDICATORS`: id, name, numerator, denominator
- `INDICATOR_GROUPS`: id, name, indicators

## Filter Syntax

DHIS2 filters use the format `property:operator:value`. Common operators:
- `eq` — Equals
- `ilike` — Case-insensitive like (contains)
- `like` — Case-sensitive like
- `in` — In a list (e.g. `id:in:[uid1,uid2]`)

## Tips

- Start with a broad query to understand available data, then narrow down
- Use `ORG_UNIT_LEVELS` first to understand the hierarchy before querying org units
- Use filters to search by name when looking for specific items
- The response includes pagination info (total_items, total_pages) for large result sets
"""

DHIS2_ANALYTICS_SKILL = """
# DHIS2 Analytics Querying

Use the `dhis2_query_analytics` tool to query aggregated analytics data.

## Parameters

- `connection_slug` (required): The slug of the DHIS2 connection to use
- `data_elements` (optional): List of data element UIDs
- `data_element_groups` (optional): List of data element group UIDs
- `indicators` (optional): List of indicator UIDs
- `indicator_groups` (optional): List of indicator group UIDs
- `org_units` (optional): List of organisation unit UIDs
- `org_unit_groups` (optional): List of organisation unit group UIDs
- `org_unit_levels` (optional): List of organisation unit level numbers (integers)
- `periods` (optional): List of period identifiers
- `include_cocs` (optional): Whether to include category option combos (default: true)

## Requirements

- At least one data dimension: `data_elements`, `data_element_groups`, `indicators`, or `indicator_groups`
- At least one org unit dimension: `org_units`, `org_unit_groups`, or `org_unit_levels`
- At least one period dimension: `periods`

## Period Format

DHIS2 uses specific period formats:
- **Yearly**: `2024`
- **Monthly**: `202401` (January 2024)
- **Quarterly**: `2024Q1`
- **Weekly**: `2024W1`
- **Daily**: `20240101`
- **Financial year (April)**: `2024April`

## Response Format

Returns a list of data points, each with:
- `dx` — Data element or indicator UID
- `pe` — Period
- `ou` — Organisation unit UID
- `co` — Category option combo UID (if include_cocs is true)
- `value` — The aggregated value

## Tips

- Query metadata first to find the correct UIDs for data elements, indicators, and org units
- Keep queries focused: the API has limits on the number of dimensions per request
  (max 50 data elements, 50 org units, 1 period per chunk — but chunking is handled automatically)
- Use org_unit_levels to get data for all units at a specific level (e.g., all districts)
"""

DHIS2_DATA_VALUES_SKILL = """
# DHIS2 Data Values Querying

Use the `dhis2_query_data_values` tool to query raw data values from DHIS2.

## Parameters

- `connection_slug` (required): The slug of the DHIS2 connection to use
- `data_elements` (optional): List of data element UIDs
- `datasets` (optional): List of dataset UIDs
- `data_element_groups` (optional): List of data element group UIDs
- `org_units` (optional): List of organisation unit UIDs
- `org_unit_groups` (optional): List of organisation unit group UIDs
- `periods` (optional): List of period identifiers
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `children` (optional): Include child org units (default: false)

## Requirements

- At least one data dimension: `data_elements`, `datasets`, or `data_element_groups`
- At least one org unit dimension: `org_units` or `org_unit_groups`
- At least one time dimension: `periods`, or both `start_date` and `end_date`

## Response Format

Returns a list of raw data values, each with:
- `dataElement` — Data element UID
- `period` — Period identifier
- `orgUnit` — Organisation unit UID
- `categoryOptionCombo` — Category option combo UID
- `attributeOptionCombo` — Attribute option combo UID
- `value` — The raw value
- `lastUpdated` — When the value was last updated

## Analytics vs Data Values

- **Analytics** (`dhis2_query_analytics`): Returns pre-aggregated data, faster, supports indicators
- **Data Values** (`dhis2_query_data_values`): Returns raw reported values, more detailed, supports datasets

Use analytics for aggregated reporting. Use data values when you need the raw submitted data.
"""

DHIS2_PYTHON_SDK_SKILL = """
# Writing Python Code with OpenHEXA DHIS2 SDK

Help users write Python code using the `openhexa.toolbox.dhis2` library.

## Basic Setup

```python
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2

# Get connection from workspace
connection = workspace.dhis2_connection("connection-slug")
dhis2 = DHIS2(connection)
```

## Metadata Queries

```python
# Get all org unit levels
levels = dhis2.meta.organisation_unit_levels()

# Get org units with pagination
result = dhis2.meta.organisation_units(page=1, pageSize=50)

# Filter metadata
elements = dhis2.meta.data_elements(
    filters=["name:ilike:malaria"],
    fields="id,name,aggregationType"
)

# Get datasets
datasets = dhis2.meta.datasets(fields="id,name")

# Get indicators
indicators = dhis2.meta.indicators(fields="id,name,numerator,denominator")
```

## Analytics Queries

```python
# Query analytics data
data = dhis2.analytics.get(
    data_elements=["element_uid1", "element_uid2"],
    org_units=["org_unit_uid"],
    periods=["202301", "202302"],
    include_cocs=True
)
# Returns: [{"dx": "...", "pe": "...", "ou": "...", "co": "...", "value": "..."}]
```

## Data Value Sets

```python
# Get raw data values
values = dhis2.data_value_sets.get(
    data_elements=["element_uid"],
    org_units=["org_unit_uid"],
    start_date="2023-01-01",
    end_date="2023-12-31"
)
```

## Working with DataFrames

```python
import pandas as pd

data = dhis2.analytics.get(
    data_elements=["uid1"],
    org_units=["uid2"],
    periods=["2024"]
)
df = pd.DataFrame(data)

# Enrich with names
df = dhis2.meta.add_dx_name_column(df)
df = dhis2.meta.add_org_unit_name_column(df)
df = dhis2.meta.add_coc_name_column(df)
df = dhis2.meta.add_org_unit_parent_columns(df)
```

## Tips for Users

- Always start by exploring metadata to find correct UIDs
- Use filters to search for specific items by name
- The SDK handles automatic pagination and chunking for large queries
- Use the DataFrame helper methods to enrich results with human-readable names
"""


def register_dhis2_skills():
    register_skill(
        name="dhis2",
        description="DHIS2 health information system integration",
        content=DHIS2_ROUTING_SKILL,
        sub_skills={
            "dhis2-metadata": DHIS2_METADATA_SKILL,
            "dhis2-analytics": DHIS2_ANALYTICS_SKILL,
            "dhis2-data-values": DHIS2_DATA_VALUES_SKILL,
            "dhis2-python-sdk": DHIS2_PYTHON_SDK_SKILL,
        },
    )
