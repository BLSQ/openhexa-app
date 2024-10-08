from ariadne import InterfaceType
from django.core.exceptions import PermissionDenied

metadata_object = InterfaceType("MetadataObject")


@metadata_object.field("attributes")
def resolve_metadata(obj, info):
    user = info.context["request"].user
    try:
        if obj.can_view_metadata(user):
            return obj.attributes.all()
    except PermissionDenied:
        return None


@metadata_object.field("targetId")
def resolve_opaque_id(obj, _):
    return obj


bindables = [metadata_object]
