from ariadne import ObjectType
from openhexa.toolbox.dhis2.api import DHIS2Error

from hexa.connections.dhis2_client_helper import get_dhis2_metadata

dhis2_connection = ObjectType("DHIS2Connection")


@dhis2_connection.field("query")
def resolve_query(dhis2_client, info, **kwargs):
    try:
        metadata = get_dhis2_metadata(
            dhis2_client,
            type=kwargs.get("type"),
            fields=kwargs.get("fields", "id,name"),
            filter=kwargs.get("filter"),
        )

        result = [{"id": item.get("id"), "name": item.get("name")} for item in metadata]
        return {"data": result, "errors": []}
    except DHIS2Error:
        return {"data": [], "errors": ["CONNECTION_ERROR"]}


bindables = [dhis2_connection]
