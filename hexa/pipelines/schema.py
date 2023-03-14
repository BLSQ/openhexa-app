import base64
import pathlib

from ariadne import EnumType, MutationType, ObjectType, QueryType, load_schema_from_path
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.workspaces.models import Workspace

from .authentication import PipelineRunUser
from .models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineVersion,
)

pipelines_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

pipeline_run_status_enum = EnumType("PipelineRunStatus", PipelineRun.STATUS_MAPPINGS)

pipeline_object = ObjectType("Pipeline")


@pipeline_object.field("runs")
def resolve_pipeline_runs(pipeline: Pipeline, info, **kwargs):
    request: HttpRequest = info.context["request"]
    qs = PipelineRun.objects.filter(pipeline=pipeline)

    order_by = kwargs.get("orderBy", None)
    if order_by is not None:
        qs = qs.order_by(order_by)
    else:
        qs = qs.order_by("-execution_date")

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


pipeline_run_object = ObjectType("PipelineRun")


@pipeline_run_object.field("triggerMode")
def resolve_pipeline_run_trigger_mode(run: PipelineRun, info, **kwargs):
    return run.trigger_mode


@pipeline_run_object.field("duration")
def resolve_pipeline_run_duration(run: PipelineRun, info, **kwargs):
    return int(run.duration.total_seconds()) if run.duration is not None else 0


@pipeline_run_object.field("config")
def resolve_pipeline_run_config(run: PipelineRun, info, **kwargs):
    return run.conf


@pipeline_run_object.field("code")
def resolve_pipeline_run_code(run: PipelineRun, info, **kwargs):
    return base64.b64encode(run.get_code()).decode("ascii")


pipeline_run_object.set_alias("progress", "current_progress")
pipeline_run_object.set_alias("logs", "run_logs")
pipeline_run_object.set_alias("version", "pipeline_version")


pipeline_version_object = ObjectType("PipelineVersion")


@pipeline_version_object.field("zipfile")
def resolve_pipeline_version_zipfile(version: PipelineVersion, info, **kwargs):
    return base64.b64encode(version.zipfile).decode("ascii")


pipelines_query = QueryType()


@pipelines_query.field("pipelines")
def resolve_pipelines(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    if kwargs.get("workspace", None):
        try:
            ws = Workspace.objects.filter_for_user(request.user).get(
                id=kwargs.get("workspace")
            )
            qs = (
                Pipeline.objects.filter_for_user(request.user)
                .filter(workspace=ws)
                .order_by("name", "id")
            )
        except Workspace.DoesNotExist:
            qs = Pipeline.objects.none()
    else:
        qs = Pipeline.objects.filter_for_user(request.user).order_by("name", "id")

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@pipelines_query.field("pipeline")
def resolve_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        if kwargs.get("id", None):
            pipeline = Pipeline.objects.filter_for_user(request.user).get(
                id=kwargs.get("id")
            )
        else:
            pipeline = Pipeline.objects.filter_for_user(request.user).get(
                name=kwargs.get("name", "")
            )
    except Pipeline.DoesNotExist:
        pipeline = None

    return pipeline


@pipelines_query.field("pipelineRun")
def resolve_pipeline_get_run(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    pipelinerun_id = kwargs.get("id")

    if pipelinerun_id != "":
        return (
            PipelineRun.objects.filter_for_user(request.user)
            .filter(id=pipelinerun_id)
            .first()
        )
    else:
        if not request.user.is_authenticated or not isinstance(
            request.user, PipelineRunUser
        ):
            return None

        try:
            pipeline_run = PipelineRun.objects.get(pk=request.user.pipeline_run.id)
        except PipelineRun.DoesNotExist:
            return None

        if pipeline_run.state in [PipelineRunState.SUCCESS, PipelineRunState.FAILED]:
            return None

        return pipeline_run


pipelines_mutations = MutationType()


@pipelines_mutations.field("createPipeline")
def resolve_create_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    qs = Pipeline.objects.filter(name=input.get("name"))
    if len(list(qs)) != 0:
        return {
            "success": False,
            "errors": ["INVALID_CONFIG"],
        }

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input.get("workspaceSlug")
        )
    except Workspace.DoesNotExist:
        return {
            "success": False,
            "errors": ["INVALID_CONFIG"],
        }

    pipeline = Pipeline.objects.create(
        name=input.get("name"),
        workspace=workspace,
    )
    return {"pipeline": pipeline, "success": True, "errors": []}


@pipelines_mutations.field("deletePipeline")
def resolve_delete_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(user=request.user).get(
            id=input.get("id")
        )
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    pipeline.delete()
    return {
        "success": True,
        "errors": [],
    }


@pipelines_mutations.field("runPipeline")
def resolve_run_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input.get("id")
        )
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    number = input.get("version", pipeline.last_version.number)
    try:
        version = PipelineVersion.objects.filter_for_user(request.user).get(
            pipeline=pipeline, number=number
        )
    except PipelineVersion.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_VERSION_NOT_FOUND"],
        }

    run = pipeline.run(
        user=request.user,
        pipeline_version=version,
        trigger_mode=PipelineRunTrigger.MANUAL,
        config=input.get("config", None),
    )

    return {
        "success": True,
        "errors": [],
        "run": run,
    }


@pipelines_mutations.field("pipelineToken")
def resolve_pipelineToken(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    qs = Pipeline.objects.filter_for_user(request.user).filter(name=input.get("name"))
    if len(list(qs)) != 1:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    return {"success": True, "errors": [], "token": qs.first().get_token()}


@pipelines_mutations.field("uploadPipeline")
def resolve_upload_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            name=input.get("name")
        )
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    try:
        newpipelineversion = pipeline.upload_new_version(
            user=request.user,
            zipfile=base64.b64decode(input.get("zipfile").encode("ascii")),
            entrypoint=input.get("entrypoint"),
            parameters=input.get("parameters"),
        )
        return {"success": True, "errors": [], "version": newpipelineversion.number}
    except Exception as e:
        return {"success": False, "errors": [str(e)]}


@pipelines_mutations.field("logPipelineMessage")
def resolve_pipeline_log_message(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    if not request.user.is_authenticated or not isinstance(
        request.user, PipelineRunUser
    ):
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    try:
        pipeline_run = PipelineRun.objects.get(pk=request.user.pipeline_run.id)
    except PipelineRun.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    if pipeline_run.state in [PipelineRunState.SUCCESS, PipelineRunState.FAILED]:
        return {
            "success": False,
            "errors": ["PIPELINE_ALREADY_COMPLETED"],
        }

    input = kwargs["input"]
    pipeline_run.log_message(input.get("priority"), input.get("message"))
    return {"success": True, "errors": []}


@pipelines_mutations.field("updatePipelineProgress")
def resolve_pipeline_progress(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    if not request.user.is_authenticated or not isinstance(
        request.user, PipelineRunUser
    ):
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    try:
        pipeline_run = PipelineRun.objects.get(pk=request.user.pipeline_run.id)
    except PipelineRun.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    if pipeline_run.state in [PipelineRunState.SUCCESS, PipelineRunState.FAILED]:
        return {
            "success": False,
            "errors": ["PIPELINE_ALREADY_COMPLETED"],
        }

    input = kwargs["input"]
    pipeline_run.progress_update(input.get("percent"))
    return {"success": True, "errors": []}


@pipelines_mutations.field("addPipelineOutput")
def resolve_pipeline_output(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    if not request.user.is_authenticated or not isinstance(
        request.user, PipelineRunUser
    ):
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    try:
        pipeline_run = PipelineRun.objects.get(pk=request.user.pipeline_run.id)
    except PipelineRun.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    if pipeline_run.state in [PipelineRunState.SUCCESS, PipelineRunState.FAILED]:
        return {
            "success": False,
            "errors": ["PIPELINE_ALREADY_COMPLETED"],
        }

    input = kwargs["input"]
    pipeline_run.add_output(input.get("output_uri"), input.get("output_type"))
    return {"success": True, "errors": []}


pipelines_bindables = [
    pipelines_query,
    pipelines_mutations,
    pipeline_object,
    pipeline_run_object,
    pipeline_run_status_enum,
    pipeline_version_object,
]
