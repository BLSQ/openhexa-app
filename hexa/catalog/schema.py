from ariadne import convert_kwargs_to_snake_case, ObjectType, QueryType, MutationType
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.templatetags.static import static
from django.conf import settings

from hexa.catalog.models import CatalogIndex, CatalogIndexType, Tag

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


@catalog_query.field("datasources")
@convert_kwargs_to_snake_case
def resolve_datasources(_, info, page, per_page=settings.GRAPHQL_PAGE_SIZE):
    request: HttpRequest = info.context["request"]
    queryset = CatalogIndex.objects.filter_for_user(request.user).filter(
        index_type=CatalogIndexType.DATASOURCE.value
    )

    paginator = Paginator(queryset, per_page)

    return {
        "page_number": page,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,
        "items": paginator.page(page),
    }


@catalog_query.field("search")
@convert_kwargs_to_snake_case
def resolve_search(_, info, page, query, per_page=settings.GRAPHQL_PAGE_SIZE):
    request: HttpRequest = info.context["request"]
    queryset = CatalogIndex.objects.filter_for_user(request.user).search(
        query, limit=100
    )

    paginator = Paginator(queryset, per_page)

    return {
        "page": page,
        "total_pages": paginator.num_pages,
        "total": paginator.count,
        "items": paginator.page(page),
    }


@catalog_query.field("tags")
def resolve_tags(*_):
    return [tag for tag in Tag.objects.all()]


# Catalog Index
catalog_index = ObjectType("CatalogIndex")
catalog_index.set_alias("type", "content_type_name")


@catalog_index.field("icon")
def resolve_icon(obj: CatalogIndex, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static(f"{obj.app_label}/img/symbol.svg"))


@catalog_index.field("detailUrl")
def resolve_detail_url(obj: CatalogIndex, *_):
    return obj.detail_url.replace("dhis2", "dhis2/catalog").replace("s3", "s3/catalog")


catalog_mutation = MutationType()


@catalog_mutation.field("catalogTagCreate")
def resolve_dhis2_instance_update(_, info, **kwargs):
    return Tag.objects.create(name=kwargs["input"]["name"])


catalog_bindables = [catalog_query, catalog_mutation, catalog_index]
