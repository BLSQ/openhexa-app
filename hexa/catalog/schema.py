from ariadne import convert_kwargs_to_snake_case, ObjectType, QueryType, MutationType
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.templatetags.static import static
from django.conf import settings

from hexa.catalog.models import CatalogIndex, CatalogIndexType, Tag
from hexa.core.graphql import result_page
from hexa.core.resolvers import resolve_tags
from hexa.plugins.connector_s3.models import Bucket

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
catalog_query.set_field("tags", resolve_tags)


@catalog_query.field("datasources")
@convert_kwargs_to_snake_case
def resolve_datasources(_, info, page, per_page=None):
    request: HttpRequest = info.context["request"]
    queryset = CatalogIndex.objects.filter_for_user(request.user).filter(
        index_type=CatalogIndexType.DATASOURCE.value
    )

    return result_page(queryset, page, per_page)


@catalog_query.field("search")
@convert_kwargs_to_snake_case
def resolve_search(_, info, page, query, per_page=None):
    request: HttpRequest = info.context["request"]
    queryset = CatalogIndex.objects.filter_for_user(request.user).search(
        query, limit=100
    )

    return result_page(queryset, page, per_page)


# Catalog Index
catalog_index = ObjectType("CatalogIndex")
catalog_index.set_alias("type", "content_type_name")


@catalog_index.field("icon")
def resolve_icon(obj: CatalogIndex, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static(f"{obj.app_label}/img/symbol.svg"))


@catalog_index.field("detailUrl")
def resolve_detail_url(obj: CatalogIndex, *_):
    if ContentType.objects.get_for_model(Bucket) == obj.content_type:
        return f"s3/{obj.object.s3_name}"

    return obj.detail_url.replace("dhis2", "dhis2/catalog").replace("s3", "s3/catalog")


catalog_mutation = MutationType()


@catalog_mutation.field("catalogTagCreate")
def resolve_dhis2_instance_update(_, info, **kwargs):
    return Tag.objects.create(name=kwargs["input"]["name"])


catalog_bindables = [catalog_query, catalog_mutation, catalog_index]
