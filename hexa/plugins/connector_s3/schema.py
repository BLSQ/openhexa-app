from ariadne import convert_kwargs_to_snake_case, QueryType, ObjectType, MutationType
from django.http import HttpRequest
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from hexa.core.resolvers import resolve_tags

from hexa.plugins.connector_s3.models import Bucket, Object
from hexa.core.graphql import result_page

s3_type_defs = """
    extend type Query {
        s3Bucket(id: String!): S3Bucket!
        s3Objects(
            bucketId: String!, 
            page: Int!,
            perPage: Int
         ): S3ObjectPage!
    }
    type S3Bucket {
        id: String!
        contentType: String!
        name: String!
        s3Name: String!
        shortName: String!
        description: String!
        url: String!
        contentSummary: String!
        countries: [Country!]
        owner: Organization
        lastSyncedAt: DateTime
        tags: [CatalogTag!]
        icon: String!
        objects(
            page: Int!,
            perPage: Int
        ): S3ObjectPage!
    }

    type S3Object {
        # Base
        id: String!
        createdAt: DateTime!
        updatedAt: DateTime!

        # RichContent
        owner: Organization
        name: String!
        shortName: String!
        description: String!
        countries: [Country!]
        locale: String!

        # Content
        tags: [CatalogTag!]

        # S3Object
        bucket: S3Bucket
        parent: S3Object
        "Path of the object within the bucket"
        s3Key: String
        s3Size: Int
        s3StorageClass: String
        "enum: 'file' or 'directory'"
        s3Type: ObjectS3Type
        s3Name: String
        s3LastModified: DateTime
        s3Extension: String

        objects(
            page: Int!,
            perPage: Int
        ): S3ObjectPage!
        
        detailUrl: String!
    }
    enum ObjectS3Type {
        file
        directory
    }
    type S3ObjectPage {
        pageNumber: Int!
        totalPages: Int!
        totalItems: Int!
        items: [S3Object!]!
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


@s3_query.field("s3Objects")
def resolve_s3_objects(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    objects_queryset = Object.objects.filter_for_user(request.user)

    return result_page(queryset=objects_queryset, page=kwargs["page"])


bucket = ObjectType("S3Bucket")
bucket.set_field("tags", resolve_tags)
bucket.set_alias("s3Name", "s3_name")


@bucket.field("icon")
def resolve_icon(obj: Bucket, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static(f"connector_s3/img/symbol.svg"))


@bucket.field("contentType")
def resolve_content_type(obj: Bucket, info):
    return _("S3 Bucket")


@bucket.field("objects")
@convert_kwargs_to_snake_case
def resolve_S3_objects(obj: Bucket, info, page, per_page=None):
    queryset = obj.object_set.filter(parent=None)
    return result_page(queryset, page, per_page)


s3_object = ObjectType("S3Object")

s3_object.set_alias("s3Key", "s3_key")
s3_object.set_alias("s3Size", "s3_size")
s3_object.set_alias("s3StorageClass", "s3_storage_class")
s3_object.set_alias("s3Type", "s3_type")
s3_object.set_alias("s3Name", "s3_name")
s3_object.set_alias("s3LastModified", "s3_last_modified")
s3_object.set_alias("s3Extension", "s3_extension")
s3_object.set_field("tags", resolve_tags)


@s3_object.field("objects")
@convert_kwargs_to_snake_case
def resolve_S3_objects_on_object(obj: Object, info, page, per_page=None):
    queryset = obj.object_set.all()
    return result_page(queryset, page, per_page)


s3_mutation = MutationType()


@s3_object.field("detailUrl")
def resolve_detail_url(obj: Object, *_):
    return f"/s3/catalog/{obj.bucket.id}/objects/{obj.id}"


@s3_mutation.field("s3BucketUpdate")
def resolve_s3_bucket_update(_, info, **kwargs):
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


s3_bindables = [s3_query, s3_mutation, bucket, s3_object]
