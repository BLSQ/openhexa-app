import base64
import pathlib

from ariadne import EnumType, MutationType, ObjectType, QueryType, load_schema_from_path
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.pipelines.models import Pipeline, PipelineCode, PipelineRun

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
def resolve_dag_run_config(run: PipelineRun, info, **kwargs):
    return run.conf


pipeline_run_object.set_alias("progress", "current_progress")
pipeline_run_object.set_alias("logs", "run_logs")

pipelines_query = QueryType()


@pipelines_query.field("pipelines")
def resolve_pipelines(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
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
    return (
        PipelineRun.objects.filter_for_user(request.user)
        .filter(id=kwargs.get("id"))
        .first()
    )


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
    pipeline = Pipeline.objects.create(
        name=input.get("name"),
        entrypoint=input.get("entrypoint"),
        parameters=input.get("parameters"),
        user=request.user,
    )
    return {"pipeline": pipeline, "success": True, "errors": []}


@pipelines_mutations.field("deletePipeline")
def resolve_delete_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter(user=request.user).get(id=input.get("id"))
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

    version = input.get("version", pipeline.last_code.version)
    try:
        code = PipelineCode.objects.filter_for_user(request.user).get(
            pipeline=pipeline, version=version
        )
    except PipelineCode.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_VERSION_NOT_FOUND"],
        }

    run = pipeline.run(
        user=request.user, pipeline_code=code, config=input.get("config", None)
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
def resolve_uploadPipeline(_, info, **kwargs):
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

    zipfile = base64.b64decode(input.get("zipfile").encode("ascii"))
    try:
        newpipelinecode = pipeline.uploadNewCode(request.user, zipfile)
        return {"success": True, "errors": [], "version": newpipelinecode.version}
    except Exception as e:
        return {"success": False, "errors": [str(e)]}


pipelines_bindables = [
    pipelines_query,
    pipelines_mutations,
    pipeline_object,
    pipeline_run_object,
    pipeline_run_status_enum,
]
