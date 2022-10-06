import pathlib
import uuid

from ariadne import (
    MutationType,
    ObjectType,
    QueryType,
    UnionType,
    convert_kwargs_to_snake_case,
    load_schema_from_path,
)
from django.http import HttpRequest

from hexa.catalog.models import Index
from hexa.core.graphql import result_page
from hexa.core.search import get_search_options, search

catalog_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

catalog_query = QueryType()

catalog_entry_object = ObjectType("CatalogEntry")
datasource_object = ObjectType("Datasource")
catalog_entry_type_object = ObjectType("CatalogEntryType")
search_result_object = ObjectType("SearchResult")
search_type_object = ObjectType("SearchType")
search_result_object_object = UnionType("SearchResultObject")


@search_result_object_object.type_resolver
def resolve_object_type(obj, info, result_type):
    if hasattr(obj, "resolve_graphql_type"):
        return obj.resolve_graphql_type(obj, info, result_type)

    return None


@catalog_entry_object.field("type")
def resolve_catalog_entry_type(index: Index, info, **kwargs):
    return {
        "id": index.content_type.id,
        "model": index.content_type.model,
        "name": index.content_type.name,
        "app": index.content_type.app_label,
    }


@catalog_entry_object.field("datasource")
def resolve_catalog_entry_datasource(index: Index, info, **kwargs):
    return {"id": index.datasource_id, "name": index.datasource_name}


@catalog_entry_object.field("objectId")
def resolve_catalog_entry_object_id(index: Index, info, **kwargs):
    return index.object_id


@catalog_entry_object.field("objectUrl")
def resolve_catalog_entry_object_url(index: Index, info, **kwargs):
    return index.object.get_absolute_url() if index.object else None


@catalog_entry_object.field("name")
def resolve_catalog_entry_name(index: Index, info, **kwargs):
    return index.display_name


@search_result_object.field("object")
def resolve_search_result_object_object(result, info, **kwargs):
    return result


@search_result_object.field("rank")
def resolve_search_result_object_rank(result, info, **kwargs):
    return getattr(result, "rank")


@catalog_query.field("search")
@convert_kwargs_to_snake_case
def resolve_search(
    _, info, query=None, page=1, per_page=15, datasource_ids=None, types=None
):
    request: HttpRequest = info.context["request"]
    if not request.user.is_authenticated:
        return {"results": [], "types": []}

    type_options, _ = get_search_options(user=request.user, query=query)

    return {
        "results": search(
            request.user,
            query,
            datasource_ids=[uuid.UUID(ds) for ds in datasource_ids]
            if datasource_ids
            else None,
            types=types,
            size=per_page,
            page=page,
        )
        if query is not None
        else [],
        "types": type_options,
    }


@catalog_query.field("catalog")
@convert_kwargs_to_snake_case
def resolve_catalog(_, info, path=None, page=1, per_page=15):
    request: HttpRequest = info.context["request"]
    queryset = Index.objects.filter_for_user(request.user).select_related(
        "content_type"
    )

    if path is None:
        queryset = queryset.roots()
    return result_page(queryset=queryset, page=page, per_page=per_page)


catalog_mutation = MutationType()


catalog_bindables = [
    catalog_query,
    catalog_mutation,
    datasource_object,
    catalog_entry_object,
    catalog_entry_type_object,
    search_result_object,
    search_type_object,
    search_result_object_object,
]
