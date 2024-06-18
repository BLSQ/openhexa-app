from ariadne import InterfaceType, UnionType
from django.core.exceptions import PermissionDenied

from hexa.datasets.models import Dataset, DatasetVersion, DatasetVersionFile

has_metadata = InterfaceType("HasMetadata")
linked_object = UnionType("LinkedObject")


@linked_object.type_resolver
def resolve_linked_object_union_type(obj, *_):
    """
    Resolver that determines which GraphQL type the linked object is.
    """
    if isinstance(obj, Dataset):
        return "Dataset"
    if isinstance(obj, DatasetVersion):
        return "DatasetVersion"
    if isinstance(obj, DatasetVersionFile):
        return "DatasetVersionFile"
    return None


@has_metadata.field("metadata")
def resolve_metadata(parent, info):
    user = info.context["request"].user
    try:
        metadata_attributes = parent.get_attributes_if_has_permission(user)
        if not metadata_attributes.exists():
            return {
                "id": parent.extended_id,
                "object": parent,
                "attributes": [],
            }

        response = {
            "id": parent.extended_id,
            "object": parent,
            "attributes": metadata_attributes,
        }
        return response
    except PermissionDenied:
        return None


@has_metadata.field("extendedId")
def resolve_extended_id(parent, info):
    return parent.extended_id


bindables = [has_metadata, linked_object]
