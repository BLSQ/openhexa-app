import pathlib

from ariadne import load_schema_from_path

from .mutations import bindables as mutations_bindables
from .types import bindables as types_bindables

files_type_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.parent.resolve()}/graphql/schema.graphql"
)

files_bindables = types_bindables + mutations_bindables
