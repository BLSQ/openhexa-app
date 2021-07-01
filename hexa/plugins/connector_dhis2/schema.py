from ariadne import QueryType, ObjectType, MutationType
from django.http import HttpRequest
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from hexa.plugins.connector_dhis2.models import Instance

dhis2_type_defs = """
    extend type Query {
        dhis2Instance(id: String!): Dhis2Instance!
    }
    type Dhis2Instance {
        id: String!
        contentType: String!
        name: String!
        shortName: String!
        description: String!
        url: String!
        contentSummary: String!
        countries: [Country!]
        owner: Organization
        lastSyncedAt: DateTime
        tags: [CatalogTag!]
        icon: String!
    }
    input Dhis2InstanceInput {
        name: String
        shortName: String
        countries: [String!]
    }
    extend type Mutation {
        dhis2InstanceUpdate(id: String!, instance: Dhis2InstanceInput!): Dhis2Instance!
    }
"""
dhis2_query = QueryType()


@dhis2_query.field("dhis2Instance")
def resolve_dhis2_instance(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    instance = Instance.objects.filter_for_user(request.user).get(pk=kwargs["id"])

    return instance


instance = ObjectType("Dhis2Instance")


@instance.field("icon")
def resolve_icon(obj: Instance, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static(f"connector_dhis2/img/symbol.svg"))


@instance.field("contentType")
def resolve_content_type(obj: Instance, info):
    return _("DHIS2 Instance")


dhis2_mutation = MutationType()


@dhis2_mutation.field("dhis2InstanceUpdate")
def resolve_dhis2_instance_update(_, info, **kwargs):
    updated_instance = Instance.objects.get(id=kwargs["id"])

    for key, value in kwargs["instance"].items():
        setattr(updated_instance, key, value)
    updated_instance.save()

    return updated_instance


dhis2_bindables = [dhis2_query, dhis2_mutation, instance]
