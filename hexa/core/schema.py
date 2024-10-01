import pathlib

from ariadne import (
    ObjectType,
    QueryType,
    load_schema_from_path,
)
from django.contrib.auth.password_validation import password_validators_help_texts

config_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

config_object = ObjectType("Config")
config_query = QueryType()


@config_query.field("config")
def resolve_config(_, info):
    return config_object


@config_object.field("passwordRequirements")
def resolve_config_password_requirements(_, info):
    return password_validators_help_texts()


config_bindables = [config_query, config_object]
