import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.countries.models import Country
from hexa.data_collections.models import Collection, CollectionElement
from hexa.tags.models import Tag
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
        queryset=Collection.objects.filter_for_user(request.user).order_by(
            "-updated_at"
        ),
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
        .prefetch_related("object")
        .filter(collection=collection)
        .order_by("-created_at")
    )

    return result_page(
        queryset=queryset, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


# Collection elements
collection_element_object = ObjectType("CollectionElement")


@collection_element_object.field("name")
def resolve_collection_element_name(element: CollectionElement, info):
    return element.object.index.display_name


@collection_element_object.field("type")
def resolve_collection_element_type(element: CollectionElement, info):
    return element.object_type.name


@collection_element_object.field("model")
def resolve_collection_element_model(element: CollectionElement, info):
    return element.object_type.model


@collection_element_object.field("app")
def resolve_collection_element_app_label(element: CollectionElement, info):
    return element.object_type.app_label


@collection_element_object.field("objectId")
def resolve_collection_element_object_id(element: CollectionElement, info):
    return element.object_id


@collection_element_object.field("url")
def resolve_collection_element_url(element: CollectionElement, info):
    try:
        return element.object.index.get_absolute_url()
    except NotImplementedError:
        return None


@collection_object.field("authorizedActions")
def resolve_collection_authorized_actions(collection: Collection, info):
    return collection


collection_authorized_actions = ObjectType("CollectionAuthorizedActions")


@collection_authorized_actions.field("canUpdate")
def resolve_collection_can_update(collection: Collection, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("data_collections.update_collection", collection)


@collection_authorized_actions.field("canDelete")
def resolve_collection_can_delete(collection: Collection, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("data_collections.delete_collection", collection)


@collections_mutations.field("createCollection")
def resolve_create_collection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        collection = Collection.objects.create_if_has_perm(
            principal,
            name=create_input["name"],
            summary=create_input.get("summary"),
            author=User.objects.get(id=create_input["authorId"])
            if "authorId" in create_input
            else principal,
            description=create_input.get("description"),
            countries=[
                Country.objects.get(code=c["code"]) for c in create_input["countries"]
            ]
            if "countries" in create_input
            else None,
        )

        return {
            "success": True,
            "collection": collection,
            "errors": [],
        }
    except PermissionError:
        return {"success": False, "collection": None, "errors": ["INVALID"]}
    except ValidationError:
        return {
            "success": False,
            "collection": None,
            "errors": ["INVALID"],
        }


@collections_mutations.field("createCollectionElement")
def resolve_create_collection_element(_, info, input, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user

    object_model = ContentType.objects.get(
        app_label=input["app"], model=input["model"]
    ).model_class()

    try:
        collection = Collection.objects.get(id=input["collectionId"])
        object = object_model.objects.filter_for_user(principal).get(
            id=input["objectId"]
        )

        element = collection.add_object(principal, object)

        return {"success": True, "element": element, "errors": []}
    except Collection.DoesNotExist:
        return {"success": False, "errors": ["COLLECTION_NOT_FOUND"]}
    except (ContentType.DoesNotExist, IntegrityError):
        return {"success": False, "errors": ["INVALID"]}
    except object_model.DoesNotExist:
        return {"success": False, "errors": ["OBJECT_NOT_FOUND"]}


@collections_mutations.field("deleteCollectionElement")
def resolve_delete_collection_element(_, info, input, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user

    try:
        element = CollectionElement.objects.get(id=input["id"])
        collection = element.collection
        element.delete_if_has_perm(principal)

        return {"success": True, "errors": [], "collection": collection}
    except CollectionElement.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}


@collections_mutations.field("updateCollection")
def resolve_update_collection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        collection = Collection.objects.filter_for_user(principal).get(
            id=update_input["id"]
        )
        collection.update_if_has_perm(
            principal,
            name=update_input.get("name", None),
            summary=update_input.get("summary", None),
            author=User.objects.get(id=update_input["authorId"])
            if "authorId" in update_input
            else None,
            countries=[
                Country.objects.get(code=c["code"]) for c in update_input["countries"]
            ]
            if "countries" in update_input
            else None,
            tags=[Tag.objects.get(pk=t) for t in update_input["tags"]]
            if "tags" in update_input
            else None,
            description=update_input.get("description", None),
        )

        return {
            "success": True,
            "collection": collection,
            "errors": [],
        }
    except Collection.DoesNotExist:
        return {"success": False, "collection": None, "errors": ["NOT_FOUND"]}
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


collections_bindables = [
    collections_query,
    collection_object,
    collection_element_object,
    collections_mutations,
    collection_authorized_actions,
]
