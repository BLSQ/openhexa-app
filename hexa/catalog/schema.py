from ariadne import MutationType, ObjectType, QueryType, convert_kwargs_to_snake_case
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.templatetags.static import static

from hexa.catalog.models import Index
from hexa.core.graphql import result_page
from hexa.plugins.connector_s3.models import Bucket
from hexa.tags.models import Tag

catalog_type_defs = """
    extend type Query {
        datasources(page: Int!, perPage: Int): CatalogIndexPage!
        search(page: Int!, perPage: Int, query: String!): CatalogIndexPage!
        tags: [CatalogTag!]
    }
    type CatalogIndexPage {
        pageNumber: Int!
        totalPages: Int!
        totalItems: Int!
        items: [CatalogIndex!]!
    }
    type CatalogIndex {
        id: String!
        objectId: String!
        name: String!
        icon: String
        externalName: String!
        indexType: CatalogIndexType
        type: String!
        contentSummary: String!
        owner: Organization!
        countries: [Country!]
        lastSyncedAt: DateTime
        detailUrl: String!
    }
    input CatalogTagInput {
        id: String
        name: String
    }
    type CatalogTag {
        id: String!
        name: String!
    }
    enum CatalogIndexType {
      DATASOURCE
      CONTENT
    }

    extend type Mutation {
        catalogTagCreate(input: CatalogTagInput!): CatalogTag!
    }
"""

catalog_query = QueryType()


@catalog_query.field("tags")
def resolve_tags(obj, *_):
    return [tag for tag in Tag.objects.all()]


@catalog_query.field("datasources")
@convert_kwargs_to_snake_case
def resolve_datasources(_, info, page, per_page=None):
    request: HttpRequest = info.context["request"]
    queryset = Index.objects.filter_for_user(request.user).roots()

    return result_page(queryset, page, per_page)


@catalog_query.field("search")
@convert_kwargs_to_snake_case
def resolve_search(_, info, page, query, per_page=None):
    request: HttpRequest = info.context["request"]
    queryset = Index.objects.filter_for_user(request.user).search(query)[:100]

    return result_page(queryset, page, per_page)


# Catalog Index
catalog_index = ObjectType("CatalogIndex")
catalog_index.set_alias("type", "content_type_name")


@catalog_index.field("icon")
def resolve_icon(obj: Index, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static(f"{obj.app_label}/img/symbol.svg"))


@catalog_index.field("detailUrl")
def resolve_detail_url(obj: Index, *_):
    # TODO: this is just a temporary workaround, we need to find a good way to handle index routing
    if ContentType.objects.get_for_model(Bucket) == obj.content_type:
        return f"s3/{obj.object.s3_name}"

    return obj.detail_url.replace("dhis2", "dhis2/catalog")


catalog_mutation = MutationType()


@catalog_mutation.field("catalogTagCreate")
def resolve_dhis2_instance_update(_, info, **kwargs):
    return Tag.objects.create(name=kwargs["input"]["name"])


catalog_bindables = [catalog_query, catalog_mutation, catalog_index]
