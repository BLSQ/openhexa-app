from ariadne import ObjectType

from hexa.connections.dhis2_connection import get_client_by_slug, get_dhis2_metadata

dhis2_connection = ObjectType("DHIS2Connection")


@dhis2_connection.field("query")
def resolve_query(connection_slug: str, info, type, filter=None, fields="id,name"):
    if not fields:
        raise ValueError("The 'fields' argument is required.")
    if not type:
        raise ValueError("The 'type' argument is required.")

    dhis2_client = get_client_by_slug(connection_slug)

    params = {}
    if filter:
        params.update(dict(param.split("=") for param in filter.split("&")))

    metadata = get_dhis2_metadata(dhis2_client, type, fields)

    result = [
        {"id": item.get("id"), "name": item.get("name")}
        for item in metadata
        if "id" in item and "name" in item
    ]
    return {"data": result}


bindables = [dhis2_connection]
