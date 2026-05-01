import csv
import io
import json

import yaml
from ariadne import QueryType
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F, OuterRef, Q, QuerySet, Subquery
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.files import storage
from hexa.files.backends.exceptions import NotFound
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineVersion,
)
from hexa.tags.models import InvalidTag, Tag
from hexa.workspaces.models import Workspace

MAX_CHOICES_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

pipelines_query = QueryType()


@pipelines_query.field("pipelines")
def resolve_pipelines(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    search = kwargs.get("search", "")

    pipelines = (
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
        pipelines = pipelines.filter(functional_type=kwargs.get("functional_type"))

    workspace_slug = kwargs.get("workspace_slug")
    ws = None
    if workspace_slug:
        try:
            ws = Workspace.objects.filter_for_user(request.user).get(
                slug=workspace_slug
            )
            pipelines = pipelines.filter(workspace=ws)
        except Workspace.DoesNotExist:
            pipelines = Pipeline.objects.none()

    tags = kwargs.get("tags", [])
    if tags:
        try:
            tag_objects = Tag.from_names(tags)
            if ws:
                tag_objects = tag_objects.filter(pipelines__workspace=ws).distinct()
            pipelines = pipelines.filter_by_tags(tag_objects)
        except InvalidTag:
            pipelines = Pipeline.objects.none()

    order_by = kwargs.get("order_by")
    if order_by:
        base_field = order_by.lstrip("-")

        if base_field == "last_run_date":
            pipelines = _order_by_last_run_date(pipelines, order_by, base_field)
        elif base_field in Pipeline.UNIQUE_SORT_FIELDS:
            pipelines = pipelines.order_by(order_by, "id")
        else:
            pipelines = pipelines.order_by(order_by, "name", "id")
    else:
        pipelines = pipelines.order_by("name", "id")

    last_run_states = kwargs.get("last_run_states")
    if last_run_states:
        last_run_status = [
            PipelineRun.REVERSE_STATUS_MAPPINGS[state] for state in last_run_states
        ]

        last_run_state_subquery = (
            PipelineRun.objects.filter(pipeline=OuterRef("pk"))
            .order_by("-execution_date")
            .values("state")[:1]
        )
        pipelines = pipelines.annotate(
            last_run_status=Subquery(last_run_state_subquery)
        ).filter(last_run_status__in=last_run_status)

    if "name" in kwargs:
        name_to_order_by = kwargs.get("name")
        search_vector = SearchVector("name")
        search_query = SearchQuery(name_to_order_by)
        pipelines = pipelines.annotate(
            rank=SearchRank(search_vector, search_query)
        ).order_by("-rank", "name", "id")

    return result_page(
        queryset=pipelines, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


def _order_by_last_run_date(
    pipelines: QuerySet, order_by: str, base_field: str
) -> QuerySet:
    latest_run_subquery = (
        PipelineRun.objects.filter(pipeline=OuterRef("pk"))
        .order_by("-execution_date")
        .values("execution_date")[:1]
    )
    pipelines = pipelines.annotate(
        last_run_date=Subquery(latest_run_subquery),
    )
    if order_by.startswith("-"):
        pipelines = pipelines.order_by(F(base_field).desc(nulls_last=True))
    else:
        pipelines = pipelines.order_by(F(base_field).asc(nulls_last=True))
    return pipelines


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


@pipelines_query.field("pipelineParameterChoices")
def resolve_pipeline_parameter_choices(_, info, workspace_slug, pipeline_version_id, parameter_code):
    request: HttpRequest = info.context["request"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(slug=workspace_slug)
    except Workspace.DoesNotExist:
        raise ValueError(f"Workspace '{workspace_slug}' not found.")

    try:
        version = PipelineVersion.objects.get(id=pipeline_version_id)
    except PipelineVersion.DoesNotExist:
        raise ValueError(f"Pipeline version '{pipeline_version_id}' not found.")

    if not request.user.has_perm("pipelines.view_pipeline_version", version):
        raise PermissionError("You do not have permission to view this pipeline version.")

    param = next(
        (p for p in version.parameters if p.get("code") == parameter_code),
        None,
    )
    if param is None:
        raise ValueError(f"Parameter '{parameter_code}' not found in pipeline version.")

    file_choices = param.get("file_choices")
    if file_choices is None:
        raise ValueError(f"Parameter '{parameter_code}' does not have dynamic file choices.")

    path = file_choices["path"]
    fmt = file_choices["format"]
    column = file_choices.get("column")

    if workspace.bucket_name is None:
        raise ValueError("Workspace does not have a file storage bucket.")

    try:
        obj = storage.get_bucket_object(workspace.bucket_name, path)
    except NotFound:
        raise ValueError(f"Choices file '{path}' not found in workspace storage.")

    if obj.size > MAX_CHOICES_FILE_SIZE:
        raise ValueError(
            f"Choices file '{path}' is too large ({obj.size} bytes). Maximum allowed size is {MAX_CHOICES_FILE_SIZE} bytes."
        )

    raw = storage.read_object(workspace.bucket_name, path)
    text = raw.decode("utf-8")

    if fmt == "csv":
        return _parse_csv_choices(text, column, path)
    elif fmt == "json":
        return _parse_json_choices(text, column, path)
    elif fmt == "yaml":
        return _parse_yaml_choices(text, column, path)
    else:
        raise ValueError(f"Unsupported file format '{fmt}'.")


def _parse_csv_choices(text: str, column: str | None, path: str) -> list[str]:
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames or []

    if not fieldnames:
        raise ValueError(f"CSV file '{path}' is empty or has no header row.")

    if column is None:
        if len(fieldnames) > 1:
            raise ValueError(
                f"CSV file '{path}' has multiple columns ({', '.join(fieldnames)}). "
                "Specify a column in the FileChoices definition."
            )
        column = fieldnames[0]
    elif column not in fieldnames:
        raise ValueError(
            f"Column '{column}' not found in CSV file '{path}'. "
            f"Available columns: {', '.join(fieldnames)}."
        )

    return [row[column] for row in reader if row.get(column) is not None]


def _parse_json_choices(text: str, column: str | None, path: str) -> list[str]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON file '{path}': {e}.")

    if not isinstance(data, list):
        raise ValueError(f"JSON file '{path}' must contain a top-level array.")

    if not data:
        raise ValueError(f"JSON file '{path}' contains an empty array.")

    if isinstance(data[0], dict):
        if column is None:
            keys = list(data[0].keys())
            if len(keys) > 1:
                raise ValueError(
                    f"JSON file '{path}' contains objects with multiple keys ({', '.join(keys)}). "
                    "Specify a column in the FileChoices definition."
                )
            column = keys[0]
        return [str(item[column]) for item in data if column in item]
    else:
        return [str(item) for item in data]


def _parse_yaml_choices(text: str, column: str | None, path: str) -> list[str]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ValueError(f"Could not parse YAML file '{path}': {e}.")

    if not isinstance(data, list):
        raise ValueError(f"YAML file '{path}' must contain a top-level sequence.")

    if not data:
        raise ValueError(f"YAML file '{path}' contains an empty sequence.")

    if isinstance(data[0], dict):
        if column is None:
            keys = list(data[0].keys())
            if len(keys) > 1:
                raise ValueError(
                    f"YAML file '{path}' contains mappings with multiple keys ({', '.join(keys)}). "
                    "Specify a column in the FileChoices definition."
                )
            column = keys[0]
        return [str(item[column]) for item in data if column in item]
    else:
        return [str(item) for item in data]


bindables = [
    pipelines_query,
]
