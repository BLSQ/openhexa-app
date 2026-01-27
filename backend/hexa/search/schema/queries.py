from ariadne import QueryType
from django.db.models import Case, FloatField, QuerySet, Value, When

from hexa.core.graphql import result_page
from hexa.databases.utils import get_database_definition
from hexa.datasets.models import Dataset
from hexa.files import storage
from hexa.pipeline_templates.models import PipelineTemplate
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import Organization
from hexa.workspaces.models import Workspace

search_query = QueryType()


def apply_scored_search(queryset: QuerySet, fields: list[str], query: str):
    if not query:
        return queryset.none()

    score_cases = [
        When(**{f"{field}__iexact": query}, then=Value(1.0)) for field in fields
    ] + [When(**{f"{field}__icontains": query}, then=Value(0.5)) for field in fields]

    pk_scores = dict(
        queryset.annotate(
            score=Case(*score_cases, default=Value(0), output_field=FloatField())
        )
        .filter(score__gt=0)
        .order_by("pk", "-score")
        .distinct("pk")
        .values_list("pk", "score")
    )

    if not pk_scores:
        return queryset.none()

    return (
        queryset.filter(pk__in=pk_scores)
        .annotate(
            score=Case(
                *[When(pk=pk, then=Value(s)) for pk, s in pk_scores.items()],
                output_field=FloatField(),
            )
        )
        .order_by("-score")
    )


def page_result_with_scores(queryset: QuerySet, page, per_page, key):
    result = result_page(queryset=queryset, page=page, per_page=per_page)
    result["items"] = [
        {key: item, "score": getattr(item, "score", 0.0)} for item in result["items"]
    ]
    return result


@search_query.field("searchDatasets")
def resolve_search_datasets(
    _,
    info,
    query=None,
    page=1,
    per_page=15,
    workspace_slugs=None,
    organization_id=None,
):
    workspace_slugs = workspace_slugs or []
    if organization_id:
        workspace_slugs = Organization.objects.get(
            id=organization_id
        ).workspaces.values_list("slug", flat=True)
    request = info.context["request"]
    qs = Dataset.objects.filter_for_workspace_slugs(request.user, workspace_slugs)
    qs = apply_scored_search(qs, ["name", "slug", "description"], query)
    return page_result_with_scores(qs, page, per_page, "dataset")


@search_query.field("searchPipelines")
def resolve_search_pipelines(
    _,
    info,
    query=None,
    page=1,
    per_page=15,
    workspace_slugs=None,
    organization_id=None,
    functional_type=None,
):
    workspace_slugs = workspace_slugs or []
    if organization_id:
        workspace_slugs = Organization.objects.get(
            id=organization_id
        ).workspaces.values_list("slug", flat=True)
    request = info.context["request"]
    qs = Pipeline.objects.filter_for_workspace_slugs(request.user, workspace_slugs)
    if functional_type:
        qs = qs.filter(functional_type=functional_type)
    qs = apply_scored_search(
        qs, ["name", "code", "description", "tags__name", "functional_type"], query
    )
    return page_result_with_scores(qs, page, per_page, "pipeline")


@search_query.field("searchPipelineTemplates")
def resolve_search_pipeline_templates(
    _,
    info,
    query=None,
    page=1,
    per_page=15,
    workspace_slugs=None,
    organization_id=None,
):
    request = info.context["request"]
    workspace_slugs = workspace_slugs or []

    if organization_id:
        workspace_slugs = Organization.objects.get(
            id=organization_id
        ).workspaces.values_list("slug", flat=True)

    qs = PipelineTemplate.objects.filter_for_user(request.user)

    if organization_id:
        qs = qs.filter(workspace__organization_id=organization_id)

    qs = apply_scored_search(qs, ["name", "code", "description", "tags__name"], query)
    return page_result_with_scores(qs, page, per_page, "pipeline_template")


@search_query.field("searchDatabaseTables")
def resolve_search_database_tables(
    _,
    info,
    query=None,
    page=1,
    per_page=15,
    workspace_slugs=None,
    organization_id=None,
):
    workspace_slugs = workspace_slugs or []
    if organization_id:
        workspace_slugs = Organization.objects.get(
            id=organization_id
        ).workspaces.values_list("slug", flat=True)
    request = info.context["request"]

    tables = [
        {
            "workspace": workspace,
            "database_table": table,
            "score": 1.0 if query and table["name"].lower() == query.lower() else 0.5,
        }
        for workspace in Workspace.objects.filter_for_workspace_slugs(
            request.user, workspace_slugs
        )
        for table in get_database_definition(workspace=workspace)
        if query and query.lower() in table["name"].lower()
    ]
    return result_page(tables, page=page, per_page=per_page)


@search_query.field("searchFiles")
def resolve_search_files(
    _,
    info,
    query=None,
    page=1,
    per_page=15,
    workspace_slugs=None,
    organization_id=None,
    prefix=None,
):
    workspace_slugs = workspace_slugs or []
    if organization_id:
        workspace_slugs = Organization.objects.get(
            id=organization_id
        ).workspaces.values_list("slug", flat=True)
    request = info.context["request"]

    files = [
        {
            "workspace": workspace,
            "file": file,
            "score": 1.0 if query and query.lower() in file.name.lower() else 0.5,
        }
        for workspace in Workspace.objects.filter_for_workspace_slugs(
            request.user, workspace_slugs
        )
        if workspace.bucket_name
        for file in storage.list_bucket_objects(
            bucket_name=workspace.bucket_name,
            match_glob=f"*{query}*",
            prefix=prefix,
        ).items
    ]
    return result_page(files, page=page, per_page=per_page)


bindables = [search_query]
