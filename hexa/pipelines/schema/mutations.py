import base64

from ariadne import MutationType, convert_kwargs_to_snake_case
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest

from hexa.databases.utils import get_table_definition
from hexa.files.api import NotFound, get_storage
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import (
    InvalidTimeoutValueError,
    Pipeline,
    PipelineDoesNotSupportParametersError,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineVersion,
)
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole

pipelines_mutations = MutationType()


# ease mocking
def get_bucket_object(bucket_name, file):
    return get_storage().get_bucket_object(bucket_name, file)


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


@pipelines_mutations.field("stopPipeline")
def resolve_stop_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        pipeline_run = PipelineRun.objects.get(id=input.get("runId"))
        if pipeline_run.state in [PipelineRunState.SUCCESS, PipelineRunState.FAILED]:
            return {
                "success": False,
                "errors": ["PIPELINE_ALREADY_COMPLETED"],
            }

        if pipeline_run.state in [
            PipelineRunState.TERMINATING,
            PipelineRunState.STOPPED,
        ]:
            return {
                "success": False,
                "errors": ["PIPELINE_ALREADY_STOPPED"],
            }

        pipeline_run.stop(request.user)
        return {
            "success": True,
            "errors": [],
        }
    except PipelineRun.DoesNotExist:
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

    try:
        if input.get("versionId"):
            version = pipeline.versions.get(id=input.get("versionId"))
        else:
            version = pipeline.last_version
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
        pipeline_code = input.get("pipelineCode", input.get("code"))
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            code=pipeline_code, workspace__slug=input["workspaceSlug"]
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

        version = pipeline.upload_new_version(
            user=request.user,
            name=input.get("name"),
            description=input.get("description"),
            external_link=input.get("externalLink"),
            zipfile=base64.b64decode(input.get("zipfile").encode("ascii")),
            parameters=input["parameters"],
            timeout=input.get("timeout"),
        )
        return {
            "success": True,
            "errors": [],
            "pipeline_version": version,
            "version": version.name,  # FIXME: This is a temporary fix to not break the SDK before 1.0.43
        }
    except PipelineDoesNotSupportParametersError:
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


bindables = [pipelines_mutations]
