from ariadne import ObjectType

from hexa.connections.dhis2_client_helper import get_dhis2_metadata

dhis2_connection = ObjectType("DHIS2Connection")


@dhis2_connection.field("query")
def resolve_query(obj, info, **kwargs):
    dhis2_client = obj
    metadata = get_dhis2_metadata(
        dhis2_client,
        type=kwargs.get("type"),
        fields=kwargs.get("fields", "id,name"),
        filter=kwargs.get("filter"),
    )

    result = [
        {"id": item.get("id"), "name": item.get("name")}
        for item in metadata
        if "id" in item and "name" in item
    ]
    return {"data": result, "errors": []}


bindables = [dhis2_connection]
