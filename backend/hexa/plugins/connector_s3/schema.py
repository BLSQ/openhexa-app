from ariadne import MutationType, ObjectType, QueryType

from hexa.core.graphql import load_type_defs_from_file
from hexa.plugins.connector_s3.models import Object

base_type_defs = load_type_defs_from_file("plugins/connector_s3/graphql/schema.graphql")

query = QueryType()
mutations = MutationType()

s3_object_object = ObjectType("S3Object")


@s3_object_object.field("type")
def resolve_s3_object_type(object: Object, info):
    return object.type_display


s3_type_defs = [base_type_defs]
s3_bindables = [query, mutations, s3_object_object]
