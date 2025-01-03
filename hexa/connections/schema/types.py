import logging

from ariadne import ObjectType
from openhexa.toolbox.dhis2.api import DHIS2Error

from hexa.connections.dhis2_client_helper import query_dhis2_metadata

dhis2_connection = ObjectType("DHIS2Connection")


@dhis2_connection.field("query")
def resolve_query(dhis2_client, info, **kwargs):
    fields = ["id", "name"]

    try:
        metadata = query_dhis2_metadata(
            dhis2_client,
            type=kwargs.get("type"),
            fields=fields,
            filter=kwargs.get("filter"),
        )

        result = [{field: item.get(field) for field in fields} for item in metadata]
        return {"data": result, "success": True, "errors": []}
    except DHIS2Error as e:
        logging.error(f"DHIS2 error: {e}")
        return {"data": [], "success": False, "errors": ["CONNECTION_ERROR"]}
    except Exception as e:
        logging.error(f"Unknown error: {e}")
        return {"data": [], "success": False, "errors": ["UNKNOWN_ERROR"]}


bindables = [dhis2_connection]
