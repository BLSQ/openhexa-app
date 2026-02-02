import json
import logging

from hexa.workspaces.models import Connection, ConnectionType, Workspace
from hexa.workspaces.utils import (
    DHIS2MetadataQueryType,
    query_dhis2_metadata,
    toolbox_client_from_connection,
)

logger = logging.getLogger(__name__)

MAX_RESULTS = 500


class WorkspaceDHIS2Tools:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    def _get_connection(self, slug: str):
        try:
            return Connection.objects.get(
                workspace=self.workspace,
                slug=slug,
                connection_type=ConnectionType.DHIS2,
            )
        except Connection.DoesNotExist:
            return None

    def _get_client(self, slug: str):
        connection = self._get_connection(slug)
        if not connection:
            return None, {"error": f"DHIS2 connection '{slug}' not found in workspace"}
        try:
            client = toolbox_client_from_connection(connection)
            return client, None
        except Exception as e:
            logger.exception("Error creating DHIS2 client")
            return None, {"error": f"Failed to connect to DHIS2: {e}"}

    def list_connections(self):
        connections = Connection.objects.filter(
            workspace=self.workspace,
            connection_type=ConnectionType.DHIS2,
        )
        items = [
            {"name": c.name, "slug": c.slug, "description": c.description}
            for c in connections
        ]
        return {"connections": items, "count": len(items)}

    def query_metadata(self, connection_slug: str, query_type: str, **kwargs):
        client, error = self._get_client(connection_slug)
        if error:
            return error

        try:
            qt = DHIS2MetadataQueryType(query_type)
        except ValueError:
            valid = [t.value for t in DHIS2MetadataQueryType]
            return {
                "error": f"Invalid query_type '{query_type}'. Must be one of: {valid}"
            }

        meta_kwargs = {}
        if kwargs.get("fields"):
            meta_kwargs["fields"] = kwargs["fields"]
        if kwargs.get("filters"):
            meta_kwargs["filters"] = kwargs["filters"]
        if kwargs.get("page") is not None:
            meta_kwargs["page"] = kwargs["page"]
        if kwargs.get("page_size") is not None:
            meta_kwargs["pageSize"] = kwargs["page_size"]

        try:
            result = query_dhis2_metadata(client, qt, **meta_kwargs)
            items = result.items[:MAX_RESULTS]
            return {
                "items": _make_json_safe(items),
                "total_items": result.total_items,
                "total_pages": result.total_pages,
                "page": result.page_number,
            }
        except Exception as e:
            logger.exception("Error querying DHIS2 metadata")
            return {"error": f"DHIS2 metadata query failed: {e}"}

    def query_analytics(self, connection_slug: str, **kwargs):
        client, error = self._get_client(connection_slug)
        if error:
            return error

        analytics_kwargs = {}
        for key in [
            "data_elements",
            "data_element_groups",
            "indicators",
            "indicator_groups",
            "org_units",
            "org_unit_groups",
            "org_unit_levels",
            "periods",
        ]:
            if key in kwargs and kwargs[key]:
                analytics_kwargs[key] = kwargs[key]

        if "include_cocs" in kwargs and kwargs["include_cocs"] is not None:
            analytics_kwargs["include_cocs"] = kwargs["include_cocs"]

        has_data = any(
            k in analytics_kwargs
            for k in [
                "data_elements",
                "data_element_groups",
                "indicators",
                "indicator_groups",
            ]
        )
        has_org = any(
            k in analytics_kwargs
            for k in ["org_units", "org_unit_groups", "org_unit_levels"]
        )
        has_period = "periods" in analytics_kwargs

        if not has_data:
            return {
                "error": "At least one data dimension required (data_elements, data_element_groups, indicators, or indicator_groups)"
            }
        if not has_org:
            return {
                "error": "At least one org unit dimension required (org_units, org_unit_groups, or org_unit_levels)"
            }
        if not has_period:
            return {"error": "periods is required"}

        try:
            data = client.analytics.get(**analytics_kwargs)
            items = data[:MAX_RESULTS]
            return {
                "data": _make_json_safe(items),
                "count": len(items),
                "total_count": len(data),
                "truncated": len(data) > MAX_RESULTS,
            }
        except Exception as e:
            logger.exception("Error querying DHIS2 analytics")
            return {"error": f"DHIS2 analytics query failed: {e}"}

    def query_data_values(self, connection_slug: str, **kwargs):
        client, error = self._get_client(connection_slug)
        if error:
            return error

        dv_kwargs = {}
        for key in [
            "data_elements",
            "datasets",
            "data_element_groups",
            "org_units",
            "org_unit_groups",
            "periods",
            "start_date",
            "end_date",
        ]:
            if key in kwargs and kwargs[key]:
                dv_kwargs[key] = kwargs[key]

        if "children" in kwargs and kwargs["children"] is not None:
            dv_kwargs["children"] = kwargs["children"]

        has_data = any(
            k in dv_kwargs for k in ["data_elements", "datasets", "data_element_groups"]
        )
        has_org = any(k in dv_kwargs for k in ["org_units", "org_unit_groups"])
        has_time = "periods" in dv_kwargs or (
            "start_date" in dv_kwargs and "end_date" in dv_kwargs
        )

        if not has_data:
            return {
                "error": "At least one data dimension required (data_elements, datasets, or data_element_groups)"
            }
        if not has_org:
            return {
                "error": "At least one org unit dimension required (org_units or org_unit_groups)"
            }
        if not has_time:
            return {
                "error": "A time dimension is required (periods, or start_date and end_date)"
            }

        try:
            data = client.data_value_sets.get(**dv_kwargs)
            items = data[:MAX_RESULTS]
            return {
                "data": _make_json_safe(items),
                "count": len(items),
                "total_count": len(data),
                "truncated": len(data) > MAX_RESULTS,
            }
        except Exception as e:
            logger.exception("Error querying DHIS2 data values")
            return {"error": f"DHIS2 data values query failed: {e}"}


def _make_json_safe(obj):
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        if isinstance(obj, list):
            return [_make_json_safe(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: _make_json_safe(v) for k, v in obj.items()}
        else:
            return str(obj)
