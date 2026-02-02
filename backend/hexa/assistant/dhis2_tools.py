def get_skill_tool():
    return {
        "name": "get_skill_details",
        "description": (
            "Get detailed guidance for a specific skill topic. "
            "Returns domain knowledge and usage patterns for the requested sub-skill."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": (
                        "The name of the sub-skill to get details for "
                        "(e.g. 'dhis2-metadata', 'dhis2-analytics', 'dhis2-data-values', 'dhis2-python-sdk')"
                    ),
                }
            },
            "required": ["skill_name"],
        },
        "requires_approval": False,
    }


def get_dhis2_tools():
    return [
        {
            "name": "list_dhis2_connections",
            "description": "List available DHIS2 connections in the workspace.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "requires_approval": False,
        },
        {
            "name": "dhis2_query_metadata",
            "description": (
                "Query DHIS2 metadata such as organisation units, data elements, "
                "indicators, datasets, and more. Use get_skill_details with "
                "'dhis2-metadata' for detailed usage guidance."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "connection_slug": {
                        "type": "string",
                        "description": "Slug of the DHIS2 connection to use",
                    },
                    "query_type": {
                        "type": "string",
                        "enum": [
                            "ORG_UNITS",
                            "ORG_UNIT_GROUPS",
                            "ORG_UNIT_LEVELS",
                            "DATASETS",
                            "DATA_ELEMENTS",
                            "DATA_ELEMENT_GROUPS",
                            "INDICATORS",
                            "INDICATOR_GROUPS",
                        ],
                        "description": "Type of metadata to query",
                    },
                    "fields": {
                        "type": "string",
                        "description": "Comma-separated field names to include (e.g. 'id,name,level')",
                    },
                    "filters": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "DHIS2 API filters (e.g. ['name:ilike:malaria'])",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for paginated results",
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of results per page",
                    },
                },
                "required": ["connection_slug", "query_type"],
            },
            "requires_approval": False,
        },
        {
            "name": "dhis2_query_analytics",
            "description": (
                "Query aggregated analytics data from DHIS2. Requires at least one "
                "data dimension (data_elements/indicators), one org unit dimension, "
                "and one period. Use get_skill_details with 'dhis2-analytics' for guidance."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "connection_slug": {
                        "type": "string",
                        "description": "Slug of the DHIS2 connection to use",
                    },
                    "data_elements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of data element UIDs",
                    },
                    "data_element_groups": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of data element group UIDs",
                    },
                    "indicators": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of indicator UIDs",
                    },
                    "indicator_groups": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of indicator group UIDs",
                    },
                    "org_units": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of organisation unit UIDs",
                    },
                    "org_unit_groups": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of organisation unit group UIDs",
                    },
                    "org_unit_levels": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of organisation unit level numbers",
                    },
                    "periods": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of period identifiers (e.g. ['202401', '2024Q1'])",
                    },
                    "include_cocs": {
                        "type": "boolean",
                        "description": "Include category option combos (default: true)",
                    },
                },
                "required": ["connection_slug", "periods"],
            },
            "requires_approval": False,
        },
        {
            "name": "dhis2_query_data_values",
            "description": (
                "Query raw data values from DHIS2 data value sets. "
                "Use get_skill_details with 'dhis2-data-values' for guidance."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "connection_slug": {
                        "type": "string",
                        "description": "Slug of the DHIS2 connection to use",
                    },
                    "data_elements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of data element UIDs",
                    },
                    "datasets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of dataset UIDs",
                    },
                    "data_element_groups": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of data element group UIDs",
                    },
                    "org_units": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of organisation unit UIDs",
                    },
                    "org_unit_groups": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of organisation unit group UIDs",
                    },
                    "periods": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of period identifiers",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                    },
                    "children": {
                        "type": "boolean",
                        "description": "Include child org units (default: false)",
                    },
                },
                "required": ["connection_slug"],
            },
            "requires_approval": False,
        },
    ]
