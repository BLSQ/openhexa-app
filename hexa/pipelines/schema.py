import base64
import pathlib

from ariadne import (
    EnumType,
    MutationType,
    ObjectType,
    QueryType,
    UnionType,
    convert_kwargs_to_snake_case,
    load_schema_from_path,
)
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest
from django.urls import reverse
from google.api_core.exceptions import NotFound
from sentry_sdk import capture_exception

from hexa.core.graphql import result_page
from hexa.databases.utils import get_table_definition
from hexa.files.api import get_bucket_object
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole
from hexa.workspaces.schema.types import workspace_permissions

from .authentication import PipelineRunUser
from .models import (
    InvalidTimeoutValueError,
    Pipeline,
    PipelineDoesNotSupportParametersError,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineVersion,
)

pipelines_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)


@workspace_permissions.field("createPipeline")
def resolve_workspace_permissions_create_pipeline(obj: Workspace, info, **kwargs):
    request = info.context["request"]

    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.create_pipeline", obj
    )


pipeline_permissions = ObjectType("PipelinePermissions")
pipeline_parameter = ObjectType("PipelineParameter")
pipeline_run_status_enum = EnumType("PipelineRunStatus", PipelineRun.STATUS_MAPPINGS)
pipeline_run_order_by_enum = EnumType(
    "PipelineRunOrderBy",
    {
        "EXECUTION_DATE_DESC": "-execution_date",
        "EXECUTION_DATE_ASC": "execution_date",
    },
)
pipeline_object = ObjectType("Pipeline")
generic_output_object = ObjectType("GenericOutput")

pipeline_run_output_union = UnionType("PipelineRunOutput")


@pipeline_run_output_union.type_resolver
def resolve_run_output_type(obj, *_):
    if "columns" in obj:
        return "DatabaseTable"
    elif obj["type"] == "file" or obj["type"] == "directory":
        return "BucketObject"

    return "GenericOutput"


@pipeline_parameter.field("name")
def resolve_pipeline_parameter_code(parameter, info, **kwargs):
    name = parameter.get("name")
    if name is None:
        name = parameter["code"]
    return name


@pipeline_parameter.field("required")
def resolve_pipeline_parameter_required(parameter, info, **kwargs):
    return parameter.get("required", False)


@pipeline_parameter.field("multiple")
def resolve_pipeline_parameter_multiple(parameter, info, **kwargs):
    return parameter.get("multiple", False)


@pipeline_permissions.field("update")
def resolve_pipeline_permissions_update(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.update_pipeline", pipeline
    )


@pipeline_permissions.field("delete")
def resolve_pipeline_permissions_delete(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.delete_pipeline", pipeline
    )


@pipeline_permissions.field("run")
def resolve_pipeline_permissions_run(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.run_pipeline", pipeline
    )


@pipeline_permissions.field("deleteVersion")
def resolve_pipeline_permissions_delete_version(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.delete_pipeline_version", pipeline
    )


@pipeline_permissions.field("schedule")
def resolve_pipeline_permissions_schedule(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return (
        request.user.is_authenticated
        and request.user.has_perm("pipelines.run_pipeline", pipeline)
        and pipeline.last_version.is_schedulable
    )


@pipeline_object.field("webhookUrl")
def resolve_pipeline_webhook_url(pipeline: Pipeline, info):
    request = info.context["request"]
    if pipeline.webhook_enabled:
        return request.build_absolute_uri(reverse("pipelines:run", args=[pipeline.id]))


@pipeline_object.field("currentVersion")
def resolve_pipeline_current_version(pipeline: Pipeline, info, **kwargs):
    return pipeline.last_version


@pipeline_object.field("permissions")
def resolve_pipeline_permissions(pipeline: Pipeline, info, **kwargs):
    return pipeline


@pipeline_object.field("versions")
def resolve_pipeline_versions(pipeline: Pipeline, info, **kwargs):
    qs = pipeline.versions.all()
    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@pipeline_object.field("runs")
def resolve_pipeline_runs(pipeline: Pipeline, info, **kwargs):
    qs = PipelineRun.objects.filter(pipeline=pipeline)

    order_by = kwargs.get("orderBy", None)
    if order_by is not None:
        qs = qs.order_by(order_by)
    else:
        qs = qs.order_by("-execution_date")

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("perPage")
    )


@pipeline_object.field("recipients")
def resolve_pipeline_recipients(pipeline: Pipeline, info, **kwargs):
    return pipeline.pipelinerecipient_set.all()


pipeline_run_object = ObjectType("PipelineRun")


@pipeline_run_object.field("triggerMode")
def resolve_pipeline_run_trigger_mode(run: PipelineRun, info, **kwargs):
    return run.trigger_mode


@pipeline_run_object.field("duration")
def resolve_pipeline_run_duration(run: PipelineRun, info, **kwargs):
    return int(run.duration.total_seconds()) if run.duration is not None else 0


@pipeline_run_object.field("config")
def resolve_pipeline_run_config(run: PipelineRun, info, **kwargs):
    return run.config


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
    if kwargs.get("workspaceSlug", None):
        try:
            ws = Workspace.objects.filter_for_user(request.user).get(
                slug=kwargs.get("workspaceSlug")
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
        return Pipeline.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Pipeline.DoesNotExist:
        return None


@pipelines_query.field("pipelineByCode")
def resolve_pipeline_by_code(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            workspace__slug=kwargs["workspaceSlug"], code=kwargs["code"]
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


@pipeline_run_object.field("outputs")
def resolve_pipeline_run_outputs(run: PipelineRun, info, **kwargs):
    result = []
    workspace = run.pipeline.workspace
    for output in run.outputs:
        try:
            if output["type"] == "file":
                result.append(
                    get_bucket_object(
                        workspace.bucket_name,
                        output["uri"][len(f"gs://{workspace.bucket_name}/") :],
                    )
                )
            elif output["type"] == "db":
                table_data = get_table_definition(workspace, output["name"])
                if table_data:
                    result.append(table_data)
                else:
                    raise Exception(
                        f"Table {output['name']} not found or connection error"
                    )
            else:
                result.append(output)
        except Exception as e:
            # Table or Bucket object might be deleted
            capture_exception(e)
            continue

    return result


@pipeline_run_object.field("datasetVersions")
def resolve_pipeline_run_dataset_version(run: PipelineRun, info, **kwargs):
    return run.dataset_versions.all()


pipelines_mutations = MutationType()


@pipelines_mutations.field("createPipeline")
def resolve_create_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input.get("workspaceSlug")
        )
    except Workspace.DoesNotExist:
        return {
            "success": False,
            "errors": ["WORKSPACE_NOT_FOUND"],
        }

    try:
        pipeline = Pipeline.objects.create(
            code=input["code"],
            name=input.get("name"),
            workspace=workspace,
        )
    except IntegrityError:
        return {"success": False, "errors": ["PIPELINE_ALREADY_EXISTS"]}

    return {"pipeline": pipeline, "success": True, "errors": []}


@pipelines_mutations.field("updatePipeline")
@convert_kwargs_to_snake_case
def resolve_update_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input.pop("id")
        )
        pipeline.update_if_has_perm(request.user, **input)
        return {"pipeline": pipeline, "success": True, "errors": []}
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["NOT_FOUND"],
        }


@pipelines_mutations.field("deletePipeline")
def resolve_delete_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(user=request.user).get(
            id=input.get("id")
        )
        pipeline.delete_if_has_perm(principal=request.user)
        return {
            "success": True,
            "errors": [],
        }
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
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

    if not request.user.has_perm("pipelines.run_pipeline", pipeline):
        raise PermissionDenied()

    try:
        run = pipeline.run(
            user=request.user,
            pipeline_version=version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config=input.get("config", {}),
            send_mail_notifications=input.get("sendMailNotifications", False),
        )
        return {
            "success": True,
            "errors": [],
            "run": run,
        }
    except ValueError:
        return {"success": False, "errors": ["INVALID_CONFIG"]}


@pipelines_mutations.field("pipelineToken")
def resolve_pipelineToken(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            code=input.get("pipelineCode"), workspace__slug=input.get("workspaceSlug")
        )
        return {"success": True, "errors": [], "token": pipeline.get_token()}
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }


@pipelines_mutations.field("uploadPipeline")
def resolve_upload_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            code=input["code"], workspace__slug=input["workspaceSlug"]
        )
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }
    try:
        if input.get("timeout") and (
            input.get("timeout") < 0
            or input.get("timeout") > int(settings.PIPELINE_RUN_MAX_TIMEOUT)
        ):
            raise InvalidTimeoutValueError(
                "Pipeline timeout value cannot be negative or greater than the maximum allowed value."
            )

        newpipelineversion = pipeline.upload_new_version(
            user=request.user,
            zipfile=base64.b64decode(input.get("zipfile").encode("ascii")),
            parameters=input["parameters"],
            timeout=input.get("timeout"),
        )
        return {"success": True, "errors": [], "version": newpipelineversion.number}
    except PipelineDoesNotSupportParametersError as e:
        return {"success": False, "errors": ["PIPELINE_DOES_NOT_SUPPORT_PARAMETERS"]}
    except InvalidTimeoutValueError:
        return {"success": False, "errors": ["INVALID_TIMEOUT_VALUE"]}
    except Exception as e:
        return {"success": False, "errors": [str(e)]}


@pipelines_mutations.field("deletePipelineVersion")
def resolve_delete_pipeline_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input["pipelineId"]
        )
        pipeline_version = PipelineVersion.objects.get(id=input["versionId"])

        if pipeline.versions.all().count() == 1:
            return {"success": False, "errors": ["PERMISSION_DENIED"]}

        if not request.user.has_perm("pipelines.delete_pipeline_version", pipeline):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}

        # Only workspace admins can delete pipeline(s) version(s) created by others
        if (
            request.user.id != pipeline_version.user.id
            and not pipeline.workspace.workspacemembership_set.filter(
                user=request.user, role=WorkspaceMembershipRole.ADMIN
            ).exists()
        ):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}

        pipeline_version.delete()
        return {
            "success": True,
            "errors": [],
        }
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }
    except PipelineVersion.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_VERSION_NOT_FOUND"],
        }


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
def resolve_add_pipeline_output(_, info, **kwargs):
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

    input = kwargs["input"]

    workspace = pipeline_run.pipeline.workspace
    if input.get("type") == "file":
        try:
            get_bucket_object(
                workspace.bucket_name,
                input["uri"][len(f"gs://{workspace.bucket_name}/") :],
            )
        except NotFound:
            return {"success": False, "errors": ["FILE_NOT_FOUND"]}
    elif input.get("type") == "db" and not get_table_definition(
        workspace, input.get("name")
    ):
        return {"success": False, "errors": ["TABLE_NOT_FOUND"]}

    pipeline_run.add_output(input["uri"], input.get("type"), input.get("name"))

    return {"success": True, "errors": []}


pipelines_bindables = [
    pipelines_query,
    pipelines_mutations,
    pipeline_object,
    pipeline_parameter,
    pipeline_run_object,
    pipeline_run_status_enum,
    pipeline_run_order_by_enum,
    pipeline_version_object,
    pipeline_permissions,
    pipeline_run_output_union,
    generic_output_object,
]
