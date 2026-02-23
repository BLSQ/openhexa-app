import base64
import io
import tempfile
from pathlib import Path
from zipfile import ZipFile

from ariadne import MutationType
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest
from django.utils import timezone
from openhexa.sdk.pipelines.exceptions import PipelineNotFound
from openhexa.sdk.pipelines.runtime import get_pipeline
from psycopg2.errors import UniqueViolation

import logging

from hexa.analytics.api import track
from hexa.databases.utils import get_table_definition
from hexa.files import storage
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.constants import UNIQUE_PIPELINE_VERSION_NAME
from hexa.pipelines.models import (
    InvalidTimeoutValueError,
    MissingPipelineConfiguration,
    Pipeline,
    PipelineCodeParsingError,
    PipelineDoesNotSupportParametersError,
    PipelineRecipient,
    PipelineRun,
    PipelineRunLogLevel,
    PipelineRunsLimitReached,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineType,
    PipelineVersion,
)
from hexa.tags.models import Tag
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

logger = logging.getLogger(__name__)

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

        if input.get("functional_type"):
            data["functional_type"] = input["functional_type"]

        tags = None
        if "tags" in input:
            tags, has_error = Tag.validate_and_get_or_create(input["tags"])
            if has_error:
                return {
                    "success": False,
                    "errors": ["INVALID_CONFIG"],
                }

        pipeline = Pipeline.objects.create_if_has_perm(
            principal=request.user, workspace=workspace, name=input["name"], **data
        )

        if tags is not None:
            pipeline.tags.set(tags)

        if pipeline.type == PipelineType.ZIPFILE:
            try:
                from hexa.pipelines.gitea import create_repository

                repo_name = create_repository(workspace.slug, pipeline.code)
                pipeline.gitea_repo_name = repo_name
                pipeline.save(update_fields=["gitea_repo_name"])
            except Exception:
                logger.exception("Failed to create Gitea repo for pipeline %s", pipeline.id)

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

        if "tags" in input:
            tags, has_error = Tag.validate_and_get_or_create(input["tags"])
            if has_error:
                return {
                    "success": False,
                    "errors": ["INVALID_CONFIG"],
                }
            input["tags"] = tags

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
    except PipelineRunsLimitReached:
        return {"success": False, "errors": ["PIPELINE_RUNS_LIMIT_REACHED"]}
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

        zipfile_data = base64.b64decode(input.get("zipfile").encode("ascii"))
        parameters = input.get("parameters")

        if not parameters:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    with ZipFile(io.BytesIO(zipfile_data), "r") as zip_file:
                        zip_file.extractall(temp_dir)

                    sdk_pipeline = get_pipeline(Path(temp_dir))
                    parameters = [p.to_dict() for p in sdk_pipeline.parameters]
            except PipelineNotFound:  # Support empty zip files
                parameters = []
            except Exception as e:
                raise PipelineCodeParsingError(str(e))
        commit_sha = None
        store_zipfile = zipfile_data
        if pipeline.gitea_repo_name:
            try:
                from hexa.pipelines.gitea import commit_zipfile as gitea_commit_zip

                author_name = request.user.display_name or request.user.email
                author_email = request.user.email
                commit_sha = gitea_commit_zip(
                    pipeline.gitea_repo_name,
                    zipfile_data,
                    input.get("name") or "Upload pipeline version",
                    author_name=author_name,
                    author_email=author_email,
                )
                store_zipfile = None
            except Exception:
                logger.exception("Failed to commit to Gitea for pipeline %s, falling back to zipfile", pipeline.id)

        version = pipeline.upload_new_version(
            user=request.user,
            name=input.get("name"),
            description=input.get("description"),
            external_link=input.get("external_link"),
            zipfile=store_zipfile,
            parameters=parameters,
            timeout=input.get("timeout"),
            config=input.get("config"),
        )
        if commit_sha:
            version.commit_sha = commit_sha
            version.save(update_fields=["commit_sha"])

        if "tags" in input:
            tags, has_error = Tag.validate_and_get_or_create(input["tags"])
            if has_error:
                return {
                    "success": False,
                    "errors": ["INVALID_CONFIG"],
                }
            pipeline.tags.set(tags)

        if "functional_type" in input:
            pipeline.functional_type = input["functional_type"]

        pipeline.save()

        return {
            "success": True,
            "errors": [],
            "pipeline_version": version,
        }
    except PipelineDoesNotSupportParametersError:
        return {"success": False, "errors": ["PIPELINE_DOES_NOT_SUPPORT_PARAMETERS"]}
    except PipelineCodeParsingError as e:
        return {
            "success": False,
            "errors": ["PIPELINE_CODE_PARSING_ERROR"],
            "details": str(e),
        }
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


@pipelines_mutations.field("updatePipelineHeartbeat")
def resolve_update_pipeline_heartbeat(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    if not request.user.is_authenticated or not isinstance(
        request.user, PipelineRunUser
    ):
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }

    pipeline_run = PipelineRun.objects.get(pk=request.user.pipeline_run.id)

    if pipeline_run.state in [
        PipelineRunState.SUCCESS,
        PipelineRunState.FAILED,
        PipelineRunState.STOPPED,
    ]:
        return {
            "success": False,
            "errors": ["PIPELINE_ALREADY_COMPLETED"],
        }
    pipeline_run.last_heartbeat = timezone.now()
    pipeline_run.save(update_fields=["last_heartbeat"])

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


def _commit_file_change(request, pipeline, operations, message):
    from hexa.pipelines.gitea import commit_files

    if not pipeline.gitea_repo_name:
        return None, "GITEA_NOT_CONFIGURED"

    if not request.user.has_perm("pipelines.update_pipeline", pipeline):
        return None, "PERMISSION_DENIED"

    author_name = request.user.display_name or request.user.email
    author_email = request.user.email

    commit_sha = commit_files(
        pipeline.gitea_repo_name,
        operations,
        message,
        author_name=author_name,
        author_email=author_email,
    )

    previous_version = pipeline.last_version
    parameters = previous_version.parameters if previous_version else []
    config = previous_version.config if previous_version else {}

    version = PipelineVersion(
        user=request.user,
        pipeline=pipeline,
        commit_sha=commit_sha,
        parameters=parameters,
        config=config,
    )
    version.save()
    return version, None


@pipelines_mutations.field("createPipelineFile")
def resolve_create_pipeline_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input["pipeline_id"]
        )
    except Pipeline.DoesNotExist:
        return {"success": False, "errors": ["PIPELINE_NOT_FOUND"]}

    try:
        version, error = _commit_file_change(
            request,
            pipeline,
            [{"path": input["file_path"], "content": input["content"]}],
            f"Create {input['file_path']}",
        )
        if error:
            return {"success": False, "errors": [error]}
        return {"success": True, "errors": [], "pipeline_version": version}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except Exception:
        logger.exception("Failed to create file in pipeline %s", pipeline.id)
        return {"success": False, "errors": ["GITEA_ERROR"]}


@pipelines_mutations.field("updatePipelineFile")
def resolve_update_pipeline_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input["pipeline_id"]
        )
    except Pipeline.DoesNotExist:
        return {"success": False, "errors": ["PIPELINE_NOT_FOUND"]}

    try:
        version, error = _commit_file_change(
            request,
            pipeline,
            [{"path": input["file_path"], "content": input["content"]}],
            f"Update {input['file_path']}",
        )
        if error:
            return {"success": False, "errors": [error]}
        return {"success": True, "errors": [], "pipeline_version": version}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except Exception:
        logger.exception("Failed to update file in pipeline %s", pipeline.id)
        return {"success": False, "errors": ["GITEA_ERROR"]}


@pipelines_mutations.field("deletePipelineFile")
def resolve_delete_pipeline_file(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input["pipeline_id"]
        )
    except Pipeline.DoesNotExist:
        return {"success": False, "errors": ["PIPELINE_NOT_FOUND"]}

    if not pipeline.gitea_repo_name:
        return {"success": False, "errors": ["GITEA_NOT_CONFIGURED"]}

    if not request.user.has_perm("pipelines.update_pipeline", pipeline):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    try:
        from hexa.pipelines.gitea import delete_file

        author_name = request.user.display_name or request.user.email
        author_email = request.user.email

        commit_sha = delete_file(
            pipeline.gitea_repo_name,
            input["file_path"],
            f"Delete {input['file_path']}",
            author_name=author_name,
            author_email=author_email,
        )

        previous_version = pipeline.last_version
        parameters = previous_version.parameters if previous_version else []
        config = previous_version.config if previous_version else {}

        version = PipelineVersion(
            user=request.user,
            pipeline=pipeline,
            commit_sha=commit_sha,
            parameters=parameters,
            config=config,
        )
        version.save()
        return {"success": True, "errors": [], "pipeline_version": version}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except Exception:
        logger.exception("Failed to delete file in pipeline %s", pipeline.id)
        return {"success": False, "errors": ["GITEA_ERROR"]}


bindables = [pipelines_mutations]
