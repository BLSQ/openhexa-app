import base64
import pathlib
from uuid import UUID

from ariadne import (
    ScalarType,
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers,
)
from django.contrib.contenttypes.models import ContentType

from hexa.core.schema import config_bindables, config_type_defs
from hexa.countries.schema import countries_bindables, countries_type_defs
from hexa.databases.schema import databases_bindables, databases_types_def
from hexa.datasets.schema import datasets_bindables, datasets_type_defs
from hexa.files.schema import files_bindables, files_type_def
from hexa.metadata.schema import metadata_bindables, metadata_type_def
from hexa.notebooks.schema import notebooks_bindables, notebooks_type_defs
from hexa.pipeline_templates.schema import (
    pipeline_templates_bindables,
    pipeline_templates_type_defs,
)
from hexa.pipelines.schema import pipelines_bindables, pipelines_type_defs
from hexa.plugins.connector_accessmod.schema import (
    accessmod_bindables,
    accessmod_type_defs,
)
from hexa.plugins.connector_airflow.schema import dags_bindables, dags_type_defs
from hexa.plugins.connector_s3.schema import s3_bindables, s3_type_defs
from hexa.tags.schema import tags_bindables, tags_type_defs
from hexa.user_management.schema import (
    identity_bindables,
    identity_directives,
    identity_type_defs,
)
from hexa.workspaces.schema import workspaces_bindables, workspaces_type_def

uuid_scalar = ScalarType("UUID")
opaque_id_scalar = ScalarType("OpaqueID")


@uuid_scalar.value_parser
def parse_uuid_value(value):
    try:
        UUID(value, version=4)
        return str(value).upper()
    except (ValueError, TypeError):
        raise ValueError(f'"{value}" is not a valid uuid')


@opaque_id_scalar.value_parser
def parse_opaque_id_value(value):
    """Decodes base64 value and returns its object instance

    Raises
    ------
        ObjectDoesNotExist: If the object instance or the content type does not exist
    """
    base64_decoded_id = base64.b64decode(value).decode("utf-8")
    instance_id, content_type_id = base64_decoded_id.split(":")
    content_type = ContentType.objects.get_for_id(content_type_id)
    model_instance = content_type.model_class().objects.get(id=instance_id)
    return model_instance


@opaque_id_scalar.serializer
def serialize_opaque_id(value):
    """Encodes object instance id and content type to base64"""
    content_type = ContentType.objects.get_for_model(value)
    value = f"{value.id}:{content_type.id}"
    return base64.b64encode(value.encode("utf-8")).decode("utf-8")


type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
schema = make_executable_schema(
    [
        type_defs,
        identity_type_defs,
        tags_type_defs,
        dags_type_defs,
        *s3_type_defs,
        accessmod_type_defs,
        countries_type_defs,
        notebooks_type_defs,
        pipelines_type_defs,
        pipeline_templates_type_defs,
        workspaces_type_def,
        metadata_type_def,
        databases_types_def,
        files_type_def,
        config_type_defs,
        datasets_type_defs,
    ],
    [
        uuid_scalar,
        opaque_id_scalar,
        *pipelines_bindables,
        *pipeline_templates_bindables,
        *identity_bindables,
        *tags_bindables,
        *dags_bindables,
        *s3_bindables,
        *accessmod_bindables,
        *countries_bindables,
        *notebooks_bindables,
        *workspaces_bindables,
        *metadata_bindables,
        *databases_bindables,
        *files_bindables,
        *datasets_bindables,
        *config_bindables,
        snake_case_fallback_resolvers,
    ],
    convert_names_case=True,
    directives=identity_directives,
)
