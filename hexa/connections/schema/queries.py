from ariadne import QueryType

from hexa.connections.dhis2_client_helper import get_client_by_slug

query = QueryType()


@query.field("dhis2connection")
def resolve_dhis2_connection(_, info, slug):
    request = info.context["request"]
    return get_client_by_slug(slug, request.user)


bindables = [query]
