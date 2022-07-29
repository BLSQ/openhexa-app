import pathlib

from ariadne import (
    InterfaceType,
    MutationType,
    ObjectType,
    QueryType,
    load_schema_from_path,
)
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.data_collections.models import Collection, CollectionElement
from hexa.user_management.models import User

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


@collection_object.field("tags")
def resolve_collection_tags(object: Collection, info):
    return object.tags.all()


@collection_object.field("elements")
def resolve_collection_elements(collection: Collection, info, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = (
        CollectionElement.objects.filter_for_user(request.user)
        .filter(collection=collection)
        .order_by("-created_at")
        .select_subclasses()
    )

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@collections_mutations.field("createCollection")
def resolve_create_collection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        collection = Collection.objects.create_if_has_perm(
            principal,
            name=create_input["name"],
            author=User.objects.get(id=create_input["authorId"])
            if "authorId" in create_input
            else None,
            description=create_input.get("description"),
        )
        # TODO: countries & tags

        return {
            "success": True,
            "collection": collection,
            "errors": [],
        }
    except ValidationError:
        return {
            "success": False,
            "collection": None,
            "errors": ["INVALID"],
        }


@collections_mutations.field("deleteCollection")
def resolve_delete_collection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        collection = Collection.objects.filter_for_user(principal).get(
            id=delete_input["id"]
        )
        collection.delete_if_has_perm(principal)

        return {
            "success": True,
            "errors": [],
        }
    except (Collection.DoesNotExist, ValidationError):
        return {
            "success": False,
            "errors": ["INVALID"],
        }


# Collection elements
collection_element_interface = InterfaceType("CollectionElement")


@collection_element_interface.type_resolver
def resolve_collection_element_type(collection_element: CollectionElement, *_):
    return collection_element.graphql_element_type


collections_bindables = [
    collections_query,
    collection_object,
    collection_element_interface,
    collections_mutations,
]
