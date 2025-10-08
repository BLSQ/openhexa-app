from ariadne import ObjectType

file_type = ObjectType("File")

# Deprecated field, maps to updated_at for backwards compatibility.
file_type.set_alias("updated", "updated_at")

bindables = [file_type]
