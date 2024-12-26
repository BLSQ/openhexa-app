from ariadne import ObjectType

from hexa.connections.dhis2_client_helper import get_client_by_slug, get_dhis2_metadata

dhis2_connection = ObjectType("DHIS2Connection")


@dhis2_connection.field("query")
def resolve_query(
    connection_slug: str,
    info,
    type: str,
    fields: str = "id,name",
    filter: str = None,
    **kwargs,
):
    if not type:
        raise ValueError("The 'type' argument is required.")

    dhis2_client = get_client_by_slug(connection_slug)
    metadata = get_dhis2_metadata(dhis2_client, type, fields=fields, filter=filter)

    result = [
        {"id": item.get("id"), "name": item.get("name")}
        for item in metadata
        if "id" in item and "name" in item
    ]
    return {"data": result}


bindables = [dhis2_connection]
