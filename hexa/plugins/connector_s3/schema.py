from ariadne import QueryType, ObjectType, MutationType
from django.http import HttpRequest
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from hexa.plugins.connector_dhis2.models import Instance
from hexa.plugins.connector_s3.models import Bucket

s3_type_defs = """
    extend type Query {
        s3Bucket(id: String!): S3Bucket!
    }
    type S3Bucket {
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
    input S3BucketInput {
        name: String
        shortName: String
        countries: [CountryInput!]
        tags: [CatalogTagInput!]
        url: String
        description: String
        owner: OrganizationInput
        s3Name: String
    }
    extend type Mutation {
        s3BucketUpdate(id: String!, input: S3BucketInput!): S3Bucket!
    }
"""
s3_query = QueryType()


@s3_query.field("s3Bucket")
def resolve_s3_bucket(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    resolved_bucket = Bucket.objects.filter_for_user(request.user).get(pk=kwargs["id"])

    return resolved_bucket


bucket = ObjectType("S3Bucket")


@bucket.field("icon")
def resolve_icon(obj: Instance, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static(f"connector_s3/img/symbol.svg"))


@bucket.field("tags")
def resolve_tags(obj: Instance, *_):
    return obj.tags.all()


@bucket.field("contentType")
def resolve_content_type(obj: Instance, info):
    return _("S3 Bucket")


s3_mutation = MutationType()


@s3_mutation.field("s3BucketUpdate")
def resolve_dhis2_instance_update(_, info, **kwargs):
    updated_bucket = Bucket.objects.get(id=kwargs["id"])
    bucket_data = kwargs["input"]

    # Obviously we need some kind of serializer here
    if "name" in bucket_data:
        updated_bucket.name = bucket_data["name"]
    if "shortName" in bucket_data:
        updated_bucket.short_name = bucket_data["shortName"]
    if "countries" in bucket_data:
        updated_bucket.countries = [
            country["code"] for country in bucket_data["countries"]
        ]
    if "tags" in bucket_data:
        updated_bucket.tags.set([tag["id"] for tag in bucket_data["tags"]])
    if "owner" in bucket_data:
        updated_bucket.owner_id = bucket_data["owner"]["id"]
    if "url" in bucket_data:
        updated_bucket.url = bucket_data["url"]
    if "description" in bucket_data:
        updated_bucket.description = bucket_data["description"]

    updated_bucket.save()

    return updated_bucket


s3_bindables = [s3_query, s3_mutation, bucket]
