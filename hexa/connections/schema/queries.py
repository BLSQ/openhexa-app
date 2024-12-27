from ariadne import QueryType

from hexa.connections.dhis2_client_helper import get_client_by_slug

query = QueryType()


@query.field("dhis2connection")
def resolve_dhis2_connection(_, info, slug):
    dhis2_client = get_client_by_slug(slug)
    return dhis2_client


bindables = [query]
