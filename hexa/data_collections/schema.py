import pathlib

from ariadne import (
    InterfaceType,
    MutationType,
    ObjectType,
    QueryType,
    load_schema_from_path,
)
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.data_collections.models import Collection, CollectionItem

collections_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
collections_query = QueryType()
collections_mutations = MutationType()


# Collections
@collections_query.field("collection")
def resolve_collection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Collection.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Collection.DoesNotExist:
        return None


@collections_query.field("collections")
def resolve_collections(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    return result_page(
        queryset=Collection.objects.filter_for_user(request.user),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("perPage"),
    )


collection_object = ObjectType("Collection")


@collection_object.field("entries")
def resolve_collection_entries(collection: Collection, info, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = (
        CollectionItem.objects.filter_for_user(request.user)
        .filter(collection=collection)
        .order_by("-created_at")
        .select_subclasses()
    )

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


# Collection entries
collection_item_interface = InterfaceType("CollectionItem")


@collection_item_interface.type_resolver
def resolve_collection_item_type(collection_item: CollectionItem, *_):
    return collection_item.graphql_item_type


collections_bindables = [
    collections_query,
    collection_object,
    collection_item_interface,
    collections_mutations,
]
