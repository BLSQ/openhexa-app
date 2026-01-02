from ariadne import QueryType
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import OuterRef, Q, Subquery
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineVersion,
)
from hexa.tags.models import InvalidTag, Tag
from hexa.workspaces.models import Workspace

pipelines_query = QueryType()


@pipelines_query.field("pipelines")
def resolve_pipelines(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    search = kwargs.get("search", "")

    qs = (
        Pipeline.objects.filter_for_user(request.user)
        .prefetch_related("tags")
        .filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(tags__name__icontains=search)
            | Q(functional_type__icontains=search)
        )
        .distinct()
    )

    if kwargs.get("functional_type"):
        qs = qs.filter(functional_type=kwargs.get("functional_type"))

    workspace_slug = kwargs.get("workspace_slug", None)
    ws = None
    if workspace_slug:
        try:
            ws = Workspace.objects.filter_for_user(request.user).get(
                slug=workspace_slug
            )
            qs = qs.filter(workspace=ws).order_by("name", "id")
        except Workspace.DoesNotExist:
            qs = Pipeline.objects.none()
    else:
        qs = qs.order_by("name", "id")

    tags = kwargs.get("tags", [])
    if tags:
        try:
            tag_objects = Tag.from_names(tags)
            if ws:
                tag_objects = tag_objects.filter(pipelines__workspace=ws).distinct()
            qs = qs.filter_by_tags(tag_objects)
        except InvalidTag:
            qs = Pipeline.objects.none()

    last_run_state = kwargs.get("last_run_state")
    if last_run_state:
        last_run_state_subquery = (
            PipelineRun.objects.filter(pipeline=OuterRef("pk"))
            .order_by("-execution_date")
            .values("state")[:1]
        )
        qs = qs.annotate(last_run_status=Subquery(last_run_state_subquery)).filter(
            last_run_status=last_run_state
        )

    if "name" in kwargs:
        name_to_order_by = kwargs.get("name")
        search_vector = SearchVector("name")
        search_query = SearchQuery(name_to_order_by)
        qs = qs.annotate(rank=SearchRank(search_vector, search_query)).order_by(
            "-rank", "name", "id"
        )

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@pipelines_query.field("pipeline")
def resolve_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        return Pipeline.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Pipeline.DoesNotExist:
        return None


@pipelines_query.field("pipelineByCode")
def resolve_pipeline_by_code(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            workspace__slug=kwargs["workspace_slug"], code=kwargs["code"]
        )
    except Pipeline.DoesNotExist:
        pipeline = None

    return pipeline


@pipelines_query.field("pipelineRun")
def resolve_pipeline_run(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    if not request.user.is_authenticated:
        return None

    run_id = kwargs["id"]
    try:
        if isinstance(request.user, PipelineRunUser):
            qs = PipelineRun.objects.filter(id=request.user.pipeline_run.id).exclude(
                state__in=[PipelineRunState.SUCCESS, PipelineRunState.FAILED]
            )
        else:
            qs = PipelineRun.objects.filter_for_user(request.user)

        return qs.get(id=run_id)

    except PipelineRun.DoesNotExist:
        return None


@pipelines_query.field("pipelineVersion")
def resolve_pipeline_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        version = PipelineVersion.objects.get(id=kwargs["id"])
        if request.user.has_perm("pipelines.view_pipeline_version", version):
            return version
    except PipelineVersion.DoesNotExist:
        return None


bindables = [
    pipelines_query,
]
