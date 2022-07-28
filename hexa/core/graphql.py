import pathlib

import stringcase
from ariadne import load_schema_from_path
from django.conf import settings
from django.core.paginator import Paginator


def load_type_defs_from_file(path: str):
    return load_schema_from_path(f"{pathlib.Path.cwd()}/hexa/{path}")


def generate_collections_type_defs_and_bindables(
    *,
    entry_type,
):
    type_defs = f"""
        type {entry_type}CollectionEntry implements CollectionEntry {{
            id: String!
            type: CollectionEntryType!
            entry: {entry_type}!
            createdAt: DateTime!
            updatedAt: DateTime!
        }}
        extend enum CollectionEntryType {{
            {stringcase.constcase(entry_type)}
        }}
    """

    bindables = []

    return type_defs, bindables


def result_page(queryset, page, per_page=None):
    if per_page is None:
        per_page = settings.GRAPHQL_DEFAULT_PAGE_SIZE
    if per_page > settings.GRAPHQL_MAX_PAGE_SIZE:
        per_page = settings.GRAPHQL_MAX_PAGE_SIZE

    paginator = Paginator(queryset, per_page)

    return {
        "page_number": page,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,
        "items": paginator.page(page),
    }
