from ariadne import QueryType
from django.http import HttpRequest

from hexa.plugins.connector_dhis2.models import Instance

dhis2_type_defs = """
    extend type Query {
        dhis2Instance(id: String!): Dhis2Instance!
    }
    type Dhis2Instance {
        id: String!
        name: String!
        description: String!
        url: String!
        contentSummary: String!
        countries: [Country!]
        owner: Organization
        lastSyncedAt: DateTime
        tags: [CatalogTag!]
    }
"""
dhis2_query = QueryType()


@dhis2_query.field("dhis2Instance")
def resolve_dhis2_instance(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    instance = Instance.objects.filter_for_user(request.user).get(pk=kwargs["id"])

    return instance


dhis2_bindables = [dhis2_query]
