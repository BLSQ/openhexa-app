from ariadne import InterfaceType
from django.core.exceptions import PermissionDenied

has_metadata = InterfaceType("MetadataObject")


@has_metadata.field("attributes")
def resolve_metadata(parent, info):
    user = info.context["request"].user
    try:
        if not parent.can_view_metadata(user):
            metadata_attributes = parent.get_attributes()
            if not metadata_attributes.exists():
                return []
            else:
                return metadata_attributes
    except PermissionDenied:
        return None


@has_metadata.field("OpaqueId")
def resolve_opaque_id(parent, info):
    return parent.opaque_id


bindables = [has_metadata]
