import logging

from ariadne import InterfaceType
from django.core.exceptions import PermissionDenied

metadata_object = InterfaceType("MetadataObject")


@metadata_object.field("attributes")
def resolve_metadata(parent, info):
    user = info.context["request"].user
    try:
        if parent.can_view_metadata(user):
            logging.info(f"{user} can view metadata {type(parent)}")
            metadata_attributes = parent.get_attributes()
            logging.info(f"Metadata attributes: {metadata_attributes}")
            return metadata_attributes if metadata_attributes.exists() else []
    except PermissionDenied:
        return None


@metadata_object.field("opaqueId")
def resolve_opaque_id(obj, info):
    # TODO move to interface resolver from global id to return db oject
    return obj.opaque_id.value


bindables = [metadata_object]
