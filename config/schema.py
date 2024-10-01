import pathlib
from uuid import UUID

from ariadne import (
    ScalarType,
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers,
)

from hexa.core.schema import config_bindables, config_type_defs
from hexa.countries.schema import countries_bindables, countries_type_defs
from hexa.databases.schema import databases_bindables, databases_types_def
from hexa.datasets.schema import datasets_bindables, datasets_type_defs
from hexa.files.schema import files_bindables, files_type_def
from hexa.notebooks.schema import notebooks_bindables, notebooks_type_defs
from hexa.pipelines.schema import pipelines_bindables, pipelines_type_defs
from hexa.plugins.connector_accessmod.schema import (
    accessmod_bindables,
    accessmod_type_defs,
)
from hexa.plugins.connector_airflow.schema import dags_bindables, dags_type_defs
from hexa.plugins.connector_dhis2.schema import dhis2_bindables, dhis2_type_defs
from hexa.plugins.connector_s3.schema import s3_bindables, s3_type_defs
from hexa.tags.schema import tags_bindables, tags_type_defs
from hexa.user_management.schema import (
    identity_bindables,
    identity_directives,
    identity_type_defs,
)
from hexa.workspaces.schema import workspaces_bindables, workspaces_type_def

uuid_scalar = ScalarType("UUID")


@uuid_scalar.value_parser
def parse_uuid_value(value):
    try:
        UUID(value, version=4)
        return str(value).upper()
    except (ValueError, TypeError):
        raise ValueError(f'"{value}" is not a valid uuid')


type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
schema = make_executable_schema(
    [
        type_defs,
        identity_type_defs,
        tags_type_defs,
        dags_type_defs,
        *dhis2_type_defs,
        *s3_type_defs,
        accessmod_type_defs,
        countries_type_defs,
        notebooks_type_defs,
        pipelines_type_defs,
        workspaces_type_def,
        databases_types_def,
        files_type_def,
        config_type_defs,
        datasets_type_defs,
    ],
    [
        uuid_scalar,
        *pipelines_bindables,
        *identity_bindables,
        *tags_bindables,
        *dags_bindables,
        *dhis2_bindables,
        *s3_bindables,
        *accessmod_bindables,
        *countries_bindables,
        *notebooks_bindables,
        *workspaces_bindables,
        *databases_bindables,
        *files_bindables,
        *datasets_bindables,
        *config_bindables,
        snake_case_fallback_resolvers,
    ],
    directives=identity_directives,
)
