from ariadne import convert_kwargs_to_snake_case, QueryType, ObjectType, MutationType
from django.http import HttpRequest
from django.template.defaultfilters import filesizeformat
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as trans

from hexa.catalog.models import Tag
from hexa.core.resolvers import resolve_tags
from hexa.plugins.connector_s3.models import Bucket, Object
from hexa.core.graphql import result_page
from hexa.user_management.models import Organization

s3_type_defs = """
    extend type Query {
        s3Bucket(id: String!): S3Bucket!
        s3Objects(
            bucketId: String!,
            path: String,
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
        message: ErrorMessage
    }

    type ErrorMessage {
        message: String
        code: String
    }
"""
s3_query = QueryType()


@s3_query.field("s3Bucket")
def resolve_s3_bucket(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    resolved_bucket = Bucket.objects.filter_for_user(request.user).get(pk=kwargs["id"])

    return resolved_bucket


@s3_query.field("s3Objects")
@convert_kwargs_to_snake_case
def resolve_s3_objects(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    objects_queryset = Object.objects.filter_for_user(
        request.user
    ).filter_by_bucket_id_and_path(kwargs["bucket_id"], kwargs.get("path", "/"))

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
    return trans("S3 Bucket")


@bucket.field("objects")
@convert_kwargs_to_snake_case
def resolve_objects(obj: Bucket, info, page, per_page=None):
    queryset = obj.object_set.filter(s3_dirname=f"{obj.s3_name}/")
    return result_page(queryset, page, per_page)


s3_object = ObjectType("S3Object")

s3_object.set_alias("s3Key", "s3_key")
s3_object.set_alias("s3Size", "s3_size")
s3_object.set_alias("s3Type", "s3_type")
s3_object.set_alias("s3LastModified", "s3_last_modified")
s3_object.set_alias("s3Extension", "s3_extension")
s3_object.set_field("tags", resolve_tags)


@s3_object.field("objects")
@convert_kwargs_to_snake_case
def resolve_S3_objects_on_object(obj: Object, info, page, per_page=None):
    queryset = obj.object_set.all()
    return result_page(queryset, page, per_page)


s3_mutation = MutationType()


@s3_object.field("name")
def resolve_file_name(obj: Object, *_):  # TODO: proper method or property on model
    if obj.s3_type == "directory":
        return obj.s3_key.rstrip("/").split("/")[-1] + "/"

    return obj.s3_key.split("/")[-1]


@s3_object.field("typeDescription")
def resolve_object_type(obj: Object, *_):
    if obj.s3_type == "directory":
        return trans("Directory")

    file_type = {
        "xlsx": "Excel file",
        "md": "Markdown document",
        "ipynb": "Jupyter Notebook",
        "csv": "CSV file",
    }.get(obj.s3_extension, "File")

    return trans(file_type)


@s3_object.field("sizeDescription")
def resolve_file_size_display(obj: Object, *_):
    return filesizeformat(obj.s3_size) if obj.s3_size > 0 else "-"


@s3_object.field("detailUrl")
def resolve_detail_url(obj: Object, *_):
    return f"/s3/catalog/{obj.bucket.id}/objects/{obj.id}"


from django import forms
from ariadne.utils import convert_camel_case_to_snake


def convert_snake_to_camel_case(snake: str):
    parts = snake.split("_")
    return "".join([x.capitalize() for x in parts])


class GraphQLForm(forms.Form):
    def __init__(self, data=None, instance=None, *args, **kwargs):
        if instance is None:
            # TODO: implement instance creation
            raise NotImplementedError("GraphQLForm must be given an instance")

        # TODO: convert back the field name in the errors to CamelCase
        # TODO: provide an escape hatch for more flexible renaming
        data = {convert_camel_case_to_snake(k): v for k, v in data.items()}
        self.instance = instance
        super().__init__(data, *args, **kwargs)

    @property
    def provided_fields(self):
        return [
            field_name for field_name in self.fields.keys() if field_name in self.data
        ]

    def save(self):
        # TODO: make GraphQLForm.save() behave like ModelForm.save() with regards to the
        # TODO: validation, clean, full_clean, ...
        # TODO: where do we handle validation looking at multiple fields at the time ?
        # HINT: look at _post_clean()
        for field_name in self.provided_fields:
            # TODO: make a check on the model field (is a M2M or not) and not on the form field
            # TODO: split model update and M2M update like in the ModelForm
            # TODO: Warn if we are setattr on something that is not a model field
            if isinstance(self.fields[field_name], forms.ModelMultipleChoiceField):
                getattr(self.instance, field_name).set(self.cleaned_data[field_name])
            else:
                setattr(self.instance, field_name, self.cleaned_data[field_name])

        self.instance.save()
        return self.instance

    @property
    def graphql_errors(self):
        return [
            {"field": convert_snake_to_camel_case(k), "message": v}
            for k, v in self.errors.get_json_data().items()
        ]


class GraphQLModelChoiceField(forms.ModelChoiceField):
    def to_python(self, value):
        # TODO: ValueError/ValidationError if not a dict ? Still accept a single id as int/str ?
        if isinstance(value, dict):
            value = value["id"]
        return super().to_python(value)


class GraphQLModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    # TODO: ValueError/ValidationError if not a list of dict ? Still accept a list of int/str ?
    def _check_values(self, value):
        value = [x["id"] for x in value if isinstance(x, dict)]
        return super()._check_values(value)


class GraphQLMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, key_name="id", *args, **kwargs):
        self.key_name = key_name
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        # TODO: ValueError/ValidationError if not a list of dict ? Still accept a list of int/str ?
        if not value:
            return []
        value = [x[self.key_name] for x in value]
        return super().to_python(value)


class GraphQLChoiceField(forms.ChoiceField):
    def __init__(self, key_name="id", *args, **kwargs):
        self.key_name = key_name
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        # TODO: ValueError/ValidationError if not a dict ? Still accept a single str/int ?
        return super().to_python(value[self.key_name])


from django_countries import countries


class BucketForm(GraphQLForm):
    name = forms.CharField(required=False, min_length=2)
    short_name = forms.CharField(required=False, min_length=2)
    tags = GraphQLModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    countries = GraphQLMultipleChoiceField(
        required=False, key_name="code", choices=dict(countries).items()
    )
    owner = GraphQLModelChoiceField(queryset=Organization.objects.all(), required=False)
    url = forms.URLField(required=False)
    description = forms.CharField(required=False)


@s3_mutation.field("s3BucketUpdate")
def resolve_s3_bucket_update(_, info, **kwargs):
    bucket = Bucket.objects.get(id=kwargs["id"])
    form = BucketForm(kwargs["input"], instance=bucket)
    if form.is_valid():
        pass
        return form.save()
    else:
        return form.graphql_errors


s3_bindables = [s3_query, s3_mutation, bucket, s3_object]
