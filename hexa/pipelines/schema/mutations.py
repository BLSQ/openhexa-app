import base64

from ariadne import MutationType
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest
from psycopg2.errors import UniqueViolation

from hexa.analytics.api import track
from hexa.databases.utils import get_table_definition
from hexa.files import storage
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.constants import UNIQUE_PIPELINE_VERSION_NAME
from hexa.pipelines.models import (
    InvalidTimeoutValueError,
    MissingPipelineConfiguration,
    Pipeline,
    PipelineDoesNotSupportParametersError,
    PipelineRecipient,
    PipelineRun,
    PipelineRunLogLevel,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineType,
    PipelineVersion,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

pipelines_mutations = MutationType()


# ease mocking
def get_bucket_object(bucket_name, file):
    return storage.get_bucket_object(bucket_name, file)


@pipelines_mutations.field("createPipeline")
def resolve_create_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input.get("workspace_slug")
        )
    except Workspace.DoesNotExist:
        return {
            "success": False,
            "errors": ["WORKSPACE_NOT_FOUND"],
        }

    try:
        data = {}
        if input.get("notebook_path", None) is not None:
            data["type"] = PipelineType.NOTEBOOK
            data["notebook_path"] = input["notebook_path"]
            # we need to check if the notebook path exist in the workspace bucket
            get_bucket_object(workspace.bucket_name, data["notebook_path"])
        else:
            data["type"] = PipelineType.ZIPFILE

        pipeline = Pipeline.objects.create_if_has_perm(
            principal=request.user, workspace=workspace, name=input["name"], **data
        )
        event_properties = {
            "pipeline_id": str(pipeline.id),
            "creation_source": (
                "CLI" if pipeline.type == PipelineType.ZIPFILE else "Notebook"
            ),
            "workspace": workspace.slug,
        }
        track(
            request,
            "pipelines.pipeline_created",
            event_properties,
        )

    except storage.exceptions.NotFound:
        return {"success": False, "errors": ["FILE_NOT_FOUND"]}

    return {"pipeline": pipeline, "success": True, "errors": []}


@pipelines_mutations.field("updatePipeline")
def resolve_update_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input.pop("id")
        )
        pipeline.update_if_has_perm(request.user, **input)
        return {"pipeline": pipeline, "success": True, "errors": []}
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except MissingPipelineConfiguration:
        return {
            "success": False,
            "errors": ["MISSING_VERSION_CONFIG"],
        }
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
        pipeline_run = PipelineRun.objects.get(id=input.get("run_id"))
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
        if input.get("version_id"):
            version = pipeline.versions.get(id=input.get("version_id"))
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
            send_mail_notifications=input.get("send_mail_notifications", False),
            log_level=(
                PipelineRunLogLevel.DEBUG
                if input.get("enable_debug_logs", False)
                else PipelineRunLogLevel.INFO
            ),
        )
        track(
            request,
            "pipelines.pipeline_run",
            {
                "pipeline_id": pipeline.code,
                "version_name": version.name if version else None,
                "trigger": PipelineRunTrigger.MANUAL,
                "workspace": pipeline.workspace.slug,
            },
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
            code=input.get("pipeline_code"), workspace__slug=input.get("workspace_slug")
        )
        return {"success": True, "errors": [], "token": pipeline.get_token()}
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }


@pipelines_mutations.field("generatePipelineWebhookUrl")
def resolve_pipeline_generate_webhook_url(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input.get("id")
        )
        if not request.user.has_perm("pipelines.update_pipeline", pipeline):
            raise PermissionDenied

        if pipeline.webhook_enabled is False:
            return {"success": False, "errors": ["WEBHOOK_NOT_ENABLED"]}

        pipeline.generate_webhook_token()
        return {"success": True, "errors": [], "pipeline": pipeline}
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


@pipelines_mutations.field("uploadPipeline")
def resolve_upload_pipeline(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        pipeline_code = input.get("pipeline_code", input.get("code"))
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            code=pipeline_code, workspace__slug=input["workspace_slug"]
        )
        if pipeline.type == PipelineType.NOTEBOOK:
            return {
                "success": False,
                "errors": ["CANNOT_UPDATE_NOTEBOOK_PIPELINE"],
            }
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
            external_link=input.get("external_link"),
            zipfile=base64.b64decode(input.get("zipfile").encode("ascii")),
            parameters=input["parameters"],
            timeout=input.get("timeout"),
            config=input.get("config"),
        )
        return {
            "success": True,
            "errors": [],
            "pipeline_version": version,
        }
    except PipelineDoesNotSupportParametersError:
        return {"success": False, "errors": ["PIPELINE_DOES_NOT_SUPPORT_PARAMETERS"]}
    except InvalidTimeoutValueError:
        return {"success": False, "errors": ["INVALID_TIMEOUT_VALUE"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except IntegrityError as e:
        if isinstance(
            e.__cause__, UniqueViolation
        ) and UNIQUE_PIPELINE_VERSION_NAME in str(e):
            return {"success": False, "errors": ["DUPLICATE_PIPELINE_VERSION_NAME"]}
        raise


@pipelines_mutations.field("updatePipelineVersion")
def resolve_update_pipeline_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        pipeline_version = PipelineVersion.objects.filter_for_user(request.user).get(
            id=input.pop("id")
        )
        pipeline_version.update_if_has_perm(request.user, **input)
        return {"pipeline_version": pipeline_version, "success": True, "errors": []}
    except PipelineVersion.DoesNotExist:
        return {
            "success": False,
            "errors": ["NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }


@pipelines_mutations.field("deletePipelineVersion")
def resolve_delete_pipeline_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline_version = PipelineVersion.objects.get(id=input["id"])

        if not request.user.has_perm(
            "pipelines.delete_pipeline_version", pipeline_version
        ):
            return {"success": False, "errors": ["PERMISSION_DENIED"]}

        pipeline_version.delete()
        return {
            "success": True,
            "errors": [],
        }
    except PipelineVersion.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_VERSION_NOT_FOUND"],
        }


@pipelines_mutations.field("addPipelineRecipient")
def resolve_add_pipeline_recipient(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input.get("pipeline_id")
        )
        user = User.objects.get(id=input["user_id"])

        recipient = PipelineRecipient.objects.create_if_has_perm(
            principal=request.user,
            pipeline=pipeline,
            user=user,
            level=input["notification_level"],
        )
        return {
            "success": True,
            "errors": [],
            "recipient": recipient,
        }
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }
    except User.DoesNotExist:
        return {
            "success": False,
            "errors": ["USER_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except IntegrityError:
        return {
            "success": False,
            "errors": ["ALREADY_EXISTS"],
        }


@pipelines_mutations.field("updatePipelineRecipient")
def resolve_update_pipeline_recipient(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        recipient = PipelineRecipient.objects.get(
            id=input["recipient_id"],
        )
        recipient.update_if_has_perm(
            principal=request.user, level=input["notification_level"]
        )
        return {
            "success": True,
            "errors": [],
            "recipient": recipient,
        }
    except PipelineRecipient.DoesNotExist:
        return {
            "success": False,
            "errors": ["RECIPIENT_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }


@pipelines_mutations.field("deletePipelineRecipient")
def resolve_delete_pipeline_recipient(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        recipient = PipelineRecipient.objects.get(
            id=input["recipient_id"],
        )
        recipient.delete_if_has_perm(principal=request.user)
        return {
            "success": True,
            "errors": [],
        }
    except PipelineRecipient.DoesNotExist:
        return {
            "success": False,
            "errors": ["RECIPIENT_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
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
        except storage.exceptions.NotFound:
            return {"success": False, "errors": ["FILE_NOT_FOUND"]}
    elif input.get("type") == "db" and not get_table_definition(
        workspace, input.get("name")
    ):
        return {"success": False, "errors": ["TABLE_NOT_FOUND"]}

    pipeline_run.add_output(input["uri"], input.get("type"), input.get("name"))

    return {"success": True, "errors": []}


@pipelines_mutations.field("upgradePipelineVersionFromTemplate")
def resolve_upgrade_pipeline_version_from_template(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input.get("pipeline_id")
        )
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }
    if not request.user.has_perm("pipelines.create_pipeline_version", pipeline):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    if not pipeline.source_template:
        return {"success": False, "errors": ["PIPELINE_NOT_FROM_TEMPLATE"]}
    if not pipeline.has_new_template_versions:
        return {"success": False, "errors": ["NO_NEW_TEMPLATE_VERSION_AVAILABLE"]}
    pipeline_version = pipeline.source_template.upgrade_pipeline(request.user, pipeline)
    return {"success": True, "errors": [], "pipeline_version": pipeline_version}


bindables = [pipelines_mutations]
