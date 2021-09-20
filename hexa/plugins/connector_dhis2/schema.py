from ariadne import MutationType, ObjectType, QueryType
from django.http import HttpRequest
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from hexa.core.resolvers import resolve_tags
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
        countries: [CountryInput!]
        tags: [CatalogTagInput!]
        url: String
        description: String
        owner: OrganizationInput
    }
    extend type Mutation {
        dhis2InstanceUpdate(id: String!, input: Dhis2InstanceInput!): Dhis2Instance!
    }
"""
dhis2_query = QueryType()


@dhis2_query.field("dhis2Instance")
def resolve_dhis2_instance(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    resolved_instance = Instance.objects.filter_for_user(request.user).get(
        pk=kwargs["id"]
    )

    return resolved_instance


instance = ObjectType("Dhis2Instance")


@instance.field("icon")
def resolve_icon(obj: Instance, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static("connector_dhis2/img/symbol.svg"))


instance.set_field("tags", resolve_tags)


@instance.field("contentType")
def resolve_content_type(obj: Instance, info):
    return _("DHIS2 Instance")


dhis2_mutation = MutationType()


@dhis2_mutation.field("dhis2InstanceUpdate")
def resolve_dhis2_instance_update(_, info, **kwargs):
    updated_instance = Instance.objects.get(id=kwargs["id"])
    instance_data = kwargs["input"]

    # Obviously we need some kind of serializer here
    if "name" in instance_data:
        updated_instance.name = instance_data["name"]
    if "shortName" in instance_data:
        updated_instance.short_name = instance_data["shortName"]
    if "countries" in instance_data:
        updated_instance.countries = [
            country["code"] for country in instance_data["countries"]
        ]
    if "tags" in instance_data:
        updated_instance.tags.set([tag["id"] for tag in instance_data["tags"]])
    if "owner" in instance_data:
        updated_instance.owner_id = instance_data["owner"]["id"]
    if "url" in instance_data:
        updated_instance.url = instance_data["url"]
    if "description" in instance_data:
        updated_instance.description = instance_data["description"]

    updated_instance.save()

    return updated_instance


dhis2_bindables = [dhis2_query, dhis2_mutation, instance]
