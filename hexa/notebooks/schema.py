import pathlib

from ariadne import QueryType, load_schema_from_path
from django.conf import settings

notebooks_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

notebooks_queries = QueryType()


@notebooks_queries.field("notebooksUrl")
def resolve_notebooks_url(_, info, **kwargs):
    return settings.NOTEBOOKS_URL


notebooks_bindables = [notebooks_queries]
