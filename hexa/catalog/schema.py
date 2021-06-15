from ariadne import convert_kwargs_to_snake_case, ObjectType
from django.core.paginator import Paginator
from django.http import HttpRequest

from hexa.catalog.models import CatalogIndex, CatalogIndexType

catalog_type_defs = """
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
        externalName: String!
        indexType: CatalogIndexType
    }
    enum CatalogIndexType {
      DATASOURCE
      CONTENT
    }
"""
catalog = ObjectType("Catalog")


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
        "items": paginator.page(1)
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
        "items": paginator.page(1)
    }
