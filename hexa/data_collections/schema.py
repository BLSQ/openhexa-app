import pathlib

from ariadne import MutationType, QueryType, load_schema_from_path
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.data_collections.models import Collection

collections_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)
collections_query = QueryType()
collections_mutations = MutationType()


@collections_query.field("collections")
def resolve_collections(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    return result_page(
        queryset=Collection.objects.filter_for_user(request.user),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("perPage"),
    )


collections_bindables = [collections_query, collections_mutations]
