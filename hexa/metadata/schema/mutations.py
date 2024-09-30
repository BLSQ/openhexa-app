from ariadne import MutationType
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

mutations = MutationType()


@mutations.field("addMetadata")
def resolve_add_metadata(_, info, **kwargs):
    mutation_input = kwargs["input"]
    user = info.context["request"].user

    try:
        model_instance = mutation_input.get("opaqueId")
        if model_instance.can_update_metadata(user):
            model_instance.add_attribute(
                key=mutation_input["key"],
                value=mutation_input.get("value", None),
                system=False,
            )

        return {"success": True, "errors": []}

    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except ContentType.DoesNotExist:
        return {"success": False, "errors": ["MODEL_TYPE_NOT_FOUND"]}
    except IntegrityError:
        return {"success": False, "errors": ["DUPLICATE_KEY"]}


@mutations.field("deleteMetadata")
def resolve_delete_metadata(_, info, **kwargs):
    mutation_input = kwargs["input"]
    user = info.context["request"].user

    try:
        model_instance = mutation_input.get("opaqueId")

        if model_instance.can_delete_metadata(user):
            deleted, _ = model_instance.delete_attribute(key=mutation_input["key"])
            if deleted > 0:
                return {"success": True, "errors": []}
        else:
            return {"success": False, "errors": ["METADATA_ATTRIBUTE_NOT_FOUND"]}

    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except ContentType.DoesNotExist:
        return {"success": False, "errors": ["MODEL_TYPE_NOT_FOUND"]}


@mutations.field("editMetadata")
def resolve_edit_metadata(_, info, **kwargs):
    mutation_input = kwargs["input"]
    user = info.context["request"].user

    try:
        model_instance = mutation_input.get("opaqueId")

        if model_instance.can_update_metadata(user):
            model_instance.update_attribute(
                key=mutation_input["key"],
                value=mutation_input["value"],
                system=False,
            )

        return {"success": True, "errors": []}

    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except ContentType.DoesNotExist:
        return {"success": False, "errors": ["MODEL_TYPE_NOT_FOUND"]}


bindables = [mutations]
