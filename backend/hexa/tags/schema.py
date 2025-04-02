import pathlib

from ariadne import ObjectType, load_schema_from_path

tags_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)


tag_object = ObjectType("Tag")

tags_bindables = [tag_object]
