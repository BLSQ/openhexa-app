import pathlib
import typing

import stringcase
from ariadne import MutationType, load_schema_from_path
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest

from hexa.catalog.models import Entry
from hexa.data_collections.models import Collection


def load_type_defs_from_file(path: str):
    return load_schema_from_path(f"{pathlib.Path.cwd()}/hexa/{path}")


def generate_collections_type_defs_and_bindables(
    config: typing.Mapping[str, typing.Type[Entry]]
):
    type_defs = []
    bindables = []

    for item_type, ItemClass in config.items():
        type_defs.append(
            f"""
            type {item_type}CollectionItem implements CollectionItem {{
                id: String!
                type: CollectionItemType!
                item: {item_type}!
                createdAt: DateTime!
                updatedAt: DateTime!
            }}
            extend enum CollectionItemType {{
                {stringcase.constcase(item_type)}
            }}
            input Add{item_type}ToCollectionInput {{
                id: String!
                collectionId: String!
            }}
            type Add{item_type}ToCollectionResult {{
                success: Boolean!
                errors: [Add{item_type}ToCollectionError!]!
                collection: Collection!
                item: {item_type}
                collectionItem: {item_type}CollectionItem
            }}
            enum Add{item_type}ToCollectionError {{
                INVALID
            }}
            extend type Mutation {{
                add{item_type}ToCollection(input: Add{item_type}ToCollectionInput!): Add{item_type}ToCollectionResult!
            }}
        """
        )

        collections_mutations = MutationType()

        @collections_mutations.field(f"add{item_type}ToCollection")
        def add_to_collection_resolver(_, info, **kwargs):
            request: HttpRequest = info.context["request"]
            principal = request.user
            add_input = kwargs["input"]

            try:
                item = ItemClass.objects.filter_for_user(principal).get(
                    id=add_input["id"]
                )
                collection = Collection.objects.filter_for_user(principal).get(
                    id=add_input["collectionId"]
                )
                collection_item = item.add_to_collection_if_has_perm(
                    principal, collection=collection
                )

                return {
                    "success": True,
                    "item": item,
                    "collection": collection,
                    "collectionItem": collection_item,
                    "errors": [],
                }
            except (ItemClass.DoesNotExist, Collection.DoesNotExist, ValidationError):
                return {
                    "success": False,
                    "item": None,
                    "collection": None,
                    "collectionItem": None,
                    "errors": ["INVALID"],
                }

        bindables.append(collections_mutations)

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
