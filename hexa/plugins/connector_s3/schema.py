from ariadne import MutationType, ObjectType, QueryType, convert_kwargs_to_snake_case
from django.http import HttpRequest
from django.template.defaultfilters import filesizeformat
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as trans

from hexa.core.graphql import result_page
from hexa.core.resolvers import resolve_tags
from hexa.plugins.connector_s3.models import Bucket, Object

s3_type_defs = """
    extend type Query {
        s3Bucket(id: String, s3Name: String): S3Bucket
        s3Object(id: String, bucketS3Name: String, s3Key: String): S3Object
        s3Objects(
            bucketS3Name: String!,
            parentS3Key: String,
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
        shortName: String!
        description: String!
        countries: [Country!]
        locale: String!

        # Content
        tags: [CatalogTag!]

        # S3Object
        bucket: S3Bucket
        "Path of the object within the bucket"
        s3Key: String
        s3Size: Int
        s3Type: ObjectS3Type
        s3LastModified: DateTime
        s3Extension: String

        objects(
            page: Int!,
            perPage: Int
        ): S3ObjectPage!

        name: String!
        typeDescription: String!
        sizeDescription: String!

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

    type S3BucketUpdateResult {
        bucket: S3Bucket
        errors: [FormError!]
    }

    type FormError {
        field: String
        message: String
        code: String
    }
"""
s3_query = QueryType()


@s3_query.field("s3Bucket")
def resolve_s3_bucket(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    if "s3Name" in kwargs:
        return Bucket.objects.filter_for_user(request.user).get(name=kwargs["s3Name"])
    elif "id" in kwargs:
        return Bucket.objects.filter_for_user(request.user).get(pk=kwargs["id"])

    return None


@s3_query.field("s3Object")
def resolve_s3_object(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    if "bucketS3Name" and "s3Key" in kwargs:
        return Object.objects.filter_for_user(request.user).get(
            bucket__name=kwargs["bucketS3Name"],
            key=f"{kwargs['bucketS3Name']}/{kwargs['s3Key']}",
        )
    elif "id" in kwargs:
        return Object.objects.filter_for_user(request.user).get(pk=kwargs["id"])

    return None


@s3_query.field("s3Objects")
def resolve_s3_objects(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = Object.objects.filter_for_user(request.user).filter(
        bucket__name=kwargs["bucketS3Name"]
    )

    if "parentS3Key" in kwargs:
        queryset = queryset.filter(
            parent_key=f"{kwargs['bucketS3Name']}/{kwargs['parentS3Key']}",
        )
    else:
        queryset = queryset.filter(
            parent_key=f"{kwargs['bucketS3Name']}/",
        )

    return result_page(queryset=queryset, page=kwargs["page"])


bucket = ObjectType("S3Bucket")
bucket.set_field("tags", resolve_tags)
bucket.set_alias("s3Name", "name")


@bucket.field("icon")
def resolve_icon(obj: Bucket, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static("connector_s3/img/symbol.svg"))


@bucket.field("contentType")
def resolve_content_type(obj: Bucket, info):
    return trans("S3 Bucket")


@bucket.field("objects")
@convert_kwargs_to_snake_case
def resolve_objects(obj: Bucket, info, page, per_page=None):
    queryset = obj.object_set.filter(parent_key=f"{obj.name}/")
    return result_page(queryset, page, per_page)


s3_object = ObjectType("S3Object")

s3_object.set_alias("s3Key", "key")
s3_object.set_alias("s3Size", "size")
s3_object.set_alias("s3Type", "type")
s3_object.set_alias("s3LastModified", "last_modified")
s3_object.set_alias("s3Extension", "extension")
s3_object.set_field("tags", resolve_tags)


@s3_object.field("objects")
@convert_kwargs_to_snake_case
def resolve_S3_objects_on_object(obj: Object, info, page, per_page=None):
    queryset = Object.objects.filter(parent_key=obj.key)
    return result_page(queryset, page, per_page)


s3_mutation = MutationType()


@s3_object.field("name")
def resolve_file_name(obj: Object, *_):  # TODO: proper method or property on model
    if obj.type == "directory":
        return obj.key.rstrip("/").split("/")[-1] + "/"

    return obj.key.split("/")[-1]


@s3_object.field("typeDescription")
def resolve_object_type(obj: Object, *_):
    if obj.type == "directory":
        return trans("Directory")

    file_type = {
        "xlsx": "Excel file",
        "md": "Markdown document",
        "ipynb": "Jupyter Notebook",
        "csv": "CSV file",
    }.get(obj.extension, "File")

    return trans(file_type)


@s3_object.field("sizeDescription")
def resolve_file_size_display(obj: Object, *_):
    return filesizeformat(obj.size) if obj.size > 0 else "-"


@s3_object.field("detailUrl")
def resolve_detail_url(obj: Object, *_):
    return f"/s3/{obj.key}"


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


# class BucketForm(GraphQLModelForm):
#     name = forms.CharField(required=False, min_length=3, empty_value=EmptyValue())
#     short_name = forms.CharField(required=False)
#     tags = GraphQLModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
#     countries = GraphQLMultipleChoiceField(
#         required=False, key_name="code", choices=dict(countries).items()
#     )
#     owner = GraphQLModelChoiceField(queryset=Organization.objects.all(), required=False)
#     url = forms.URLField(required=False)
#     description = forms.CharField(required=False)
#
#
# @s3_mutation.field("s3BucketUpdate")
# def resolve_s3_bucket_update(_, info, **kwargs):
#     bucket = Bucket.objects.get(id=kwargs["id"])
#     form = BucketForm(kwargs["input"], instance=bucket)
#     if form.is_valid():
#         return form.save()
#     else:
#         return form.graphql_errors


s3_bindables = [s3_query, s3_mutation, bucket, s3_object]
