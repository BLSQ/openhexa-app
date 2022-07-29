import pathlib

import stringcase
from ariadne import MutationType, load_schema_from_path
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
        input Add{entry_type}ToCollectionInput {{
            id: String!
        }}
        type Add{entry_type}ToCollectionResult {{
            success: Boolean!
            errors: [Add{entry_type}ToCollectionError!]!
            entry: {entry_type}CollectionEntry
        }}
        enum Add{entry_type}ToCollectionError {{
            INVALID
        }}
        extend type Mutation {{
            add{entry_type}ToCollection(input: Add{entry_type}ToCollectionInput!): Add{entry_type}ToCollectionResult!
        }}
    """

    collections_mutations = MutationType()

    @collections_mutations.field(f"add{entry_type}ToCollection")
    def add_to_collection_resolver(_, info, **kwargs):
        pass

    bindables = [collections_mutations]

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
