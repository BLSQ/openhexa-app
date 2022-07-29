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

    for element_type, ElementClass in config.items():
        type_defs.append(
            f"""
            type {element_type}CollectionElement implements CollectionElement {{
                id: String!
                type: CollectionElementType!
                element: {element_type}!
                createdAt: DateTime!
                updatedAt: DateTime!
            }}
            extend enum CollectionElementType {{
                {stringcase.constcase(element_type)}
            }}
            input Add{element_type}ToCollectionInput {{
                id: String!
                collectionId: String!
            }}
            type Add{element_type}ToCollectionResult {{
                success: Boolean!
                errors: [Add{element_type}ToCollectionError!]!
                collection: Collection
                element: {element_type}
                collectionElement: {element_type}CollectionElement
            }}
            enum Add{element_type}ToCollectionError {{
                INVALID
            }}
            input Remove{element_type}FromCollectionInput {{
                id: String!
                collectionId: String!
            }}
            type Remove{element_type}FromCollectionResult {{
                success: Boolean!
                errors: [Remove{element_type}FromCollectionError!]!
                collection: Collection
                element: {element_type}
            }}
            enum Remove{element_type}FromCollectionError {{
                INVALID
            }}
            extend type Mutation {{
                add{element_type}ToCollection(input: Add{element_type}ToCollectionInput!): Add{element_type}ToCollectionResult!
                remove{element_type}FromCollection(input: Remove{element_type}FromCollectionInput!): Remove{element_type}FromCollectionResult!
            }}
        """
        )

        collections_mutations = MutationType()

        @collections_mutations.field(f"add{element_type}ToCollection")
        def add_to_collection_resolver(_, info, **kwargs):
            request: HttpRequest = info.context["request"]
            principal = request.user
            add_input = kwargs["input"]

            try:
                element = ElementClass.objects.filter_for_user(principal).get(
                    id=add_input["id"]
                )
                collection = Collection.objects.filter_for_user(principal).get(
                    id=add_input["collectionId"]
                )
                collection_element = element.add_to_collection_if_has_perm(
                    principal, collection=collection
                )

                return {
                    "success": True,
                    "element": element,
                    "collection": collection,
                    "collectionElement": collection_element,
                    "errors": [],
                }
            except (
                ElementClass.DoesNotExist,
                Collection.DoesNotExist,
                ValidationError,
            ):
                return {
                    "success": False,
                    "element": None,
                    "collection": None,
                    "collectionElement": None,
                    "errors": ["INVALID"],
                }

        @collections_mutations.field(f"remove{element_type}FromCollection")
        def remove_from_collection_resolver(_, info, **kwargs):
            request: HttpRequest = info.context["request"]
            principal = request.user
            remove_input = kwargs["input"]

            try:
                element = ElementClass.objects.filter_for_user(principal).get(
                    id=remove_input["id"]
                )
                collection = Collection.objects.filter_for_user(principal).get(
                    id=remove_input["collectionId"]
                )
                element.remove_from_collection_if_has_perm(
                    principal, collection=collection
                )

                return {
                    "success": True,
                    "element": element,
                    "collection": collection,
                    "errors": [],
                }
            except (
                ElementClass.DoesNotExist,
                Collection.DoesNotExist,
                ValidationError,
            ):
                return {
                    "success": False,
                    "element": None,
                    "collection": None,
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
