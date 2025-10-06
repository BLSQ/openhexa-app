from ariadne import ObjectType

file_type = ObjectType("File")


@file_type.field("updated")
def resolve_updated(obj, info):
    """Deprecated field, maps to updated_at for backwards compatibility."""
    return getattr(obj, "updated_at", None)


bindables = [file_type]
