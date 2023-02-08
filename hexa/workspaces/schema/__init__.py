import pathlib

from ariadne import load_schema_from_path

from .mutations import bindables as mutations_bindables
from .queries import bindables as queries_bindables
from .types import bindables as types_bindables

workspaces_type_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.parent.resolve()}/graphql/schema.graphql"
)

workspaces_bindables = types_bindables + queries_bindables + mutations_bindables
