from ariadne import MutationType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from hexa.metadata.models import MetadataAttribute

mutations = MutationType()


@mutations.field("deleteMetadataAttribute")
def resolve_delete_metadata(_, info, **kwargs):
    mutation_input = kwargs["input"]
    user = info.context["request"].user

    try:
        model_instance = mutation_input.get("target_id")
        if model_instance.can_delete_metadata(user):
            model_instance.delete_attribute(key=mutation_input["key"])
            return {"success": True, "errors": []}
        else:
            return {"success": False, "errors": ["METADATA_ATTRIBUTE_NOT_FOUND"]}
    except ObjectDoesNotExist:
        return {"success": False, "errors": ["TARGET_NOT_FOUND"]}
    except MetadataAttribute.NotFound:
        return {"success": False, "errors": ["METADATA_ATTRIBUTE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@mutations.field("setMetadataAttribute")
def resolve_set_metadata(_, info, **kwargs):
    mutation_input = kwargs["input"]
    user = info.context["request"].user

    try:
        model_instance = mutation_input.get("target_id")
        if model_instance.can_update_metadata(user):
            attribute = model_instance.update_or_create_attribute(
                key=mutation_input["key"],
                principal=user,
                label=mutation_input.get("label", None),
                value=mutation_input["value"],
                system=False,
            )

            return {"success": True, "errors": [], "attribute": attribute}
    except ObjectDoesNotExist:
        return {"success": False, "errors": ["TARGET_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


bindables = [mutations]
