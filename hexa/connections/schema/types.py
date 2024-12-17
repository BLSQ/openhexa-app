from ariadne import ObjectType

from hexa.connections.dhis2_connection import get_dhis2_client

dhis2_connection = ObjectType("DHIS2Connection")


@dhis2_connection.field("query")
def resolve_query(connection, info, type, filter=None, fields=None):
    if not fields:
        raise ValueError("The 'fields' argument is required.")
    if not type:
        raise ValueError("The 'type' argument is required.")

    dhis2_client = get_dhis2_client(connection)

    params = {}
    if filter:
        params.update(dict(param.split("=") for param in filter.split("&")))

    # Fetch metadata
    metadata = dhis2_client.get_metadata(type=type, fields=fields, params=params)

    # Transform data to include only 'id' and 'name'
    result = [
        {"id": item.get("id"), "name": item.get("name")}
        for item in metadata
        if "id" in item and "name" in item
    ]
    return {"data": result}


bindables = [dhis2_connection]
