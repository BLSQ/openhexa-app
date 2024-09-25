from ariadne import InterfaceType
from django.core.exceptions import PermissionDenied

metadata_object = InterfaceType("MetadataObject")


@metadata_object.field("attributes")
def resolve_metadata(parent, info):
    user = info.context["request"].user
    try:
        if parent.can_view_metadata(user):
            metadata_attributes = parent.get_attributes()
            return metadata_attributes if metadata_attributes.exists() else []
    except PermissionDenied:
        return None


@metadata_object.field("OpaqueId")
def resolve_opaque_id(parent, info):
    return parent.opaque_id.value


bindables = [metadata_object]
