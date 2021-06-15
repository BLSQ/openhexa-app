from ariadne import convert_kwargs_to_snake_case, ObjectType, QueryType, MutationType
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.templatetags.static import static

from hexa.catalog.models import CatalogIndex, CatalogIndexType

catalog_type_defs = """
    extend type Query {
        catalog: Catalog!
    }
    type Catalog {
        datasources(page: Int!, perPage: Int!): CatalogIndexPage!
        search(page: Int!, perPage: Int!, query: String!): CatalogIndexPage!
    }
    type CatalogIndexPage {
        page: Int!
        totalPages: Int!
        total: Int!
        items: [CatalogIndex!]!
    }
    type CatalogIndex {
        id: String!
        name: String!
        icon: String
        externalName: String!
        indexType: CatalogIndexType
        type: String!
        contentSummary: String!
        owner: Organization!
        countries: [Country!]
        lastSyncedAt: DateTime
    }
    enum CatalogIndexType {
      DATASOURCE
      CONTENT
    }
"""
catalog_query = QueryType()
catalog_mutations = MutationType()
catalog = ObjectType("Catalog")


@catalog_query.field("catalog")
def resolve_catalog(*_):
    return {}


@catalog.field("datasources")
@convert_kwargs_to_snake_case
def resolve_datasources(_, info, page, per_page):
    request: HttpRequest = info.context["request"]
    queryset = CatalogIndex.objects.filter_for_user(request.user).filter(
        index_type=CatalogIndexType.DATASOURCE.value
    )

    paginator = Paginator(queryset, per_page)

    return {
        "page": page,
        "total_pages": paginator.num_pages,
        "total": paginator.count,
        "items": paginator.page(1),
    }


@catalog.field("search")
@convert_kwargs_to_snake_case
def resolve_search(_, info, page, per_page, query):
    request: HttpRequest = info.context["request"]
    queryset = CatalogIndex.objects.filter_for_user(request.user).search(
        query, limit=100
    )

    paginator = Paginator(queryset, per_page)

    return {
        "page": page,
        "total_pages": paginator.num_pages,
        "total": paginator.count,
        "items": paginator.page(1),
    }


# Catalog Index
catalog_index = ObjectType("CatalogIndex")
catalog_index.set_alias("type", "content_type_name")


@catalog_index.field("icon")
def resolve_icon(obj: CatalogIndex, info):
    request: HttpRequest = info.context["request"]
    return request.build_absolute_uri(static(f"{obj.app_label}/img/symbol.svg"))


catalog_bindables = [catalog_query, catalog, catalog_index]
