import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path

from hexa.plugins.connector_s3.models import Object

base_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

query = QueryType()
mutations = MutationType()

s3_object_object = ObjectType("S3Object")


@s3_object_object.field("type")
def resolve_s3_object_type(object: Object, info):
    return object.type_display


s3_type_defs = [base_type_defs]
s3_bindables = [query, mutations, s3_object_object]
