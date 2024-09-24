from ariadne import InterfaceType
from django.core.exceptions import PermissionDenied

has_metadata = InterfaceType("MetadataObject")


@has_metadata.field("attributes")
def resolve_metadata(parent, info):
    user = info.context["request"].user
    try:
        metadata_attributes = parent.get_attributes_if_has_permission(user)
        if not metadata_attributes.exists():
            return []
        else:
            return metadata_attributes
    except PermissionDenied:
        return None


@has_metadata.field("extendedId")
def resolve_extended_id(parent, info):
    return parent.extended_id


bindables = [has_metadata]
