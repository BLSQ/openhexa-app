import base64
import io
import zipfile
from pathlib import Path

from ariadne import EnumType, ObjectType, UnionType
from django.urls import reverse
from sentry_sdk import capture_exception

from hexa.core.graphql import result_page
from hexa.databases.utils import get_table_definition
from hexa.files import storage
from hexa.files.backends.base import StorageObject
from hexa.pipeline_templates.models import PipelineTemplateVersion
from hexa.pipelines.models import (
    Pipeline,
    PipelineNotificationLevel,
    PipelineRun,
    PipelineType,
    PipelineVersion,
)
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_permissions

pipeline_permissions = ObjectType("PipelinePermissions")
pipeline_version_permissions = ObjectType("PipelineVersionPermissions")
pipeline_parameter = ObjectType("PipelineParameter")
pipeline_run_status_enum = EnumType("PipelineRunStatus", PipelineRun.STATUS_MAPPINGS)
pipeline_notification_level_enum = EnumType(
    "PipelineNotificationLevel", PipelineNotificationLevel
)
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


@workspace_permissions.field("createPipeline")
def resolve_workspace_permissions_create_pipeline(obj: Workspace, info, **kwargs):
    request = info.context["request"]

    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.create_pipeline", obj
    )


@pipeline_run_output_union.type_resolver
def resolve_run_output_type(obj, *_):
    if isinstance(obj, StorageObject):
        return "BucketObject"
    elif "columns" in obj:
        return "DatabaseTable"
    else:
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


@pipeline_permissions.field("createVersion")
def resolve_pipeline_permissions_create_version(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.create_pipeline_version", pipeline
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


@pipeline_permissions.field("schedule")
def resolve_pipeline_permissions_schedule(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return bool(
        request.user.is_authenticated
        and request.user.has_perm("pipelines.schedule_pipeline", pipeline)
    )


@pipeline_permissions.field("stopPipeline")
def resolve_pipeline_permissions_stop_pipeline(pipeline: Pipeline, info, **kwargs):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.stop_pipeline", pipeline
    )


@pipeline_permissions.field("createTemplateVersion")
def resolve_pipeline_permissions_create_template_version(
    pipeline: Pipeline, info, **kwargs
):
    request = info.context["request"]
    user_has_permission = request.user.is_authenticated and request.user.has_perm(
        "pipeline_templates.create_pipeline_template_version", pipeline.workspace
    )
    current_version_has_template = pipeline.last_version and hasattr(
        pipeline.last_version, "template_version"
    )
    pipeline_is_created_from_a_template = pipeline.source_template
    pipeline_is_notebook = pipeline.type == PipelineType.NOTEBOOK
    is_allowed = (
        user_has_permission
        and not pipeline_is_created_from_a_template
        and not current_version_has_template
        and not pipeline_is_notebook
    )
    return {
        "is_allowed": is_allowed,
        "reasons": [
            msg
            for msg in [
                not user_has_permission and "PERMISSION_DENIED",
                pipeline_is_created_from_a_template
                and "PIPELINE_IS_ALREADY_FROM_TEMPLATE",
                current_version_has_template and "NO_NEW_TEMPLATE_VERSION_AVAILABLE",
                pipeline_is_notebook and "PIPELINE_IS_NOTEBOOK",
            ]
            if msg
        ],
    }


@pipeline_version_permissions.field("update")
def resolve_pipeline_version_permissions_update(
    version: PipelineVersion, info, **kwargs
):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.update_pipeline_version", version
    )


@pipeline_version_permissions.field("delete")
def resolve_pipeline_version_permissions_delete(
    version: PipelineVersion, info, **kwargs
):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipelines.delete_pipeline_version", version
    )


@pipeline_object.field("webhookUrl")
def resolve_pipeline_webhook_url(pipeline: Pipeline, info):
    request = info.context["request"]
    if pipeline.webhook_enabled:
        return request.build_absolute_uri(
            reverse("pipelines:run", args=[pipeline.webhook_token])
        )


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
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@pipeline_object.field("template")
def resolve_pipeline_template(pipeline: Pipeline, info, **kwargs):
    template = getattr(pipeline, "template", None)
    return template if template and not template.is_deleted else None


@pipeline_object.field("sourceTemplate")
def resolve_source_template(pipeline: Pipeline, info, **kwargs):
    return (
        pipeline.source_template
        if pipeline.source_template and not pipeline.source_template.is_deleted
        else None
    )


@pipeline_object.field("newTemplateVersions")
def resolve_new_template_versions(pipeline: Pipeline, info, **kwargs):
    return PipelineTemplateVersion.objects.get_updates_for(pipeline)


@pipeline_object.field("hasNewTemplateVersions")
def resolve_has_new_template_versions(pipeline: Pipeline, info, **kwargs):
    return pipeline.has_new_template_versions


@pipeline_object.field("runs")
def resolve_pipeline_runs(pipeline: Pipeline, info, **kwargs):
    qs = PipelineRun.objects.filter(pipeline=pipeline)

    order_by = kwargs.get("order_by", None)
    if order_by is not None:
        qs = qs.order_by(order_by)
    else:
        qs = qs.order_by("-execution_date")

    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@pipeline_object.field("recipients")
def resolve_pipeline_recipients(pipeline: Pipeline, info, **kwargs):
    return pipeline.pipelinerecipient_set.all()


@pipeline_object.field("tags")
def resolve_pipeline_tags(pipeline: Pipeline, info, **kwargs):
    return pipeline.tags.all()


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
    code = run.get_code()
    if code is None:
        return None
    return base64.b64encode(code).decode("ascii")


pipeline_run_object.set_alias("progress", "current_progress")
pipeline_run_object.set_alias("logs", "run_logs")
pipeline_run_object.set_alias("version", "pipeline_version")


@pipeline_run_object.field("hasErrorMessages")
def resolve_pipeline_run_has_error_messages(run: PipelineRun, info, **kwargs):
    if not run.messages:
        return False
    return any(msg.get("priority") in ("ERROR", "CRITICAL") for msg in run.messages)


def get_language_from_path(path: str) -> str:
    """Get language from file path extension."""
    extension = Path(path).suffix
    supported_languages = {
        ".py": "python",
        ".json": "json",
        ".ipynb": "jupyter",
        ".R": "r",
        ".r": "r",
        ".md": "markdown",
        ".sql": "sql",
    }
    return supported_languages.get(extension, "text")


pipeline_version_object = ObjectType("PipelineVersion")


@pipeline_version_object.field("versionName")
def resolve_pipeline_version_version_name(version: PipelineVersion, info, **kwargs):
    return version.version_name


pipeline_version_object.set_alias("number", "versionNumber")
pipeline_version_object.set_alias("commitSha", "commit_sha")


@pipeline_version_object.field("isLatestVersion")
def resolve_pipeline_version_is_latest(version: PipelineVersion, info, **kwargs):
    return version.is_latest_version


@pipeline_version_object.field("zipfile")
def resolve_pipeline_version_zipfile(version: PipelineVersion, info, **kwargs):
    if version.commit_sha and version.pipeline.gitea_repo_name:
        from hexa.pipelines.gitea import get_archive_zip

        archive = get_archive_zip(version.pipeline.gitea_repo_name, version.commit_sha)
        return base64.b64encode(archive).decode("ascii")
    if version.zipfile:
        return base64.b64encode(version.zipfile).decode("ascii")
    return None


def _build_files_dict_from_entries(version_name, entries):
    """Build the files dict from a list of (path, is_dir, content_bytes|None) tuples."""
    files_dict = {}

    for path, is_dir, content_bytes in entries:
        path = path.rstrip("/")
        parts = path.split("/")
        for i in range(1, len(parts)):
            parent_path = "/".join(parts[:i])
            if parent_path not in files_dict:
                files_dict[parent_path] = {
                    "id": version_name + "/" + parent_path,
                    "name": parts[i - 1],
                    "path": parent_path,
                    "type": "directory",
                    "content": None,
                    "parent_id": "/".join([version_name] + parts[: i - 1])
                    if i > 1
                    else None,
                    "auto_select": False,
                    "language": None,
                    "line_count": None,
                }

        if path not in files_dict:
            content = None
            language = None
            line_count = None
            if not is_dir and content_bytes is not None:
                try:
                    content = content_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    content = None
                language = get_language_from_path(path)
                line_count = content.count("\n") + 1 if content else 0
            files_dict[path] = {
                "id": version_name + "/" + path,
                "name": path.split("/")[-1] if "/" in path else path,
                "path": path,
                "type": "directory" if is_dir else "file",
                "content": content,
                "parent_id": "/".join([version_name] + path.split("/")[:-1])
                if "/" in path
                else None,
                "auto_select": False,
                "language": language,
                "line_count": line_count,
            }

    return files_dict


def _auto_select_and_sort(files_dict):
    all_files = sorted(files_dict.values(), key=lambda f: f["name"].lower())
    file_candidates = [f for f in all_files if f["type"] == "file"]

    if file_candidates:

        def get_file_priority(file_name):
            if file_name in ["main.py", "__main__.py", "pipeline.py"]:
                return 1
            elif file_name.endswith(".py"):
                return 2
            return 3

        auto_select_file = min(
            file_candidates, key=lambda f: get_file_priority(f["name"])
        )
        auto_select_file["auto_select"] = True

    return all_files


@pipeline_version_object.field("files")
def resolve_pipeline_version_files(version: PipelineVersion, info, **kwargs):
    """Extract and return flattened file structure."""
    if version.commit_sha and version.pipeline.gitea_repo_name:
        return _resolve_files_from_gitea(version)

    if not version.zipfile:
        return []

    return _resolve_files_from_zipfile(version)


def _resolve_files_from_gitea(version: PipelineVersion):
    from hexa.pipelines.gitea import get_archive_zip

    archive_bytes = get_archive_zip(
        version.pipeline.gitea_repo_name, version.commit_sha
    )
    entries = []
    with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as zf:
        for entry in zf.infolist():
            # Gitea archives contain a top-level directory; strip it
            path = entry.filename
            parts = path.split("/", 1)
            if len(parts) > 1:
                path = parts[1]
            else:
                continue
            if not path:
                continue
            if entry.is_dir():
                entries.append((path, True, None))
            else:
                entries.append((path, False, zf.read(entry.filename)))

    files_dict = _build_files_dict_from_entries(version.version_name, entries)
    return _auto_select_and_sort(files_dict)


def _resolve_files_from_zipfile(version: PipelineVersion):
    entries = []
    with zipfile.ZipFile(io.BytesIO(version.zipfile), "r") as zip_file:
        for zip_entry in zip_file.infolist():
            path = zip_entry.filename
            if zip_entry.is_dir():
                entries.append((path, True, None))
            else:
                entries.append((path, False, zip_file.read(zip_entry.filename)))

    files_dict = _build_files_dict_from_entries(version.version_name, entries)
    return _auto_select_and_sort(files_dict)


@pipeline_version_object.field("permissions")
def resolve_pipeline_version_permissions(version: PipelineVersion, info, **kwargs):
    return version


@pipeline_version_object.field("templateVersion")
def resolve_pipeline_version_template_version(version: PipelineVersion, info, **kwargs):
    return version.template_version if hasattr(version, "template_version") else None


@pipeline_run_object.field("outputs")
def resolve_pipeline_run_outputs(run: PipelineRun, info, **kwargs):
    result = []
    workspace = run.pipeline.workspace
    for output in run.outputs:
        try:
            if output["type"] == "file":
                result.append(
                    storage.get_bucket_object(
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
        except storage.exceptions.NotFound:
            # File object might be deleted
            continue
        except Exception as e:
            # Table or Bucket object might be deleted
            capture_exception(e)

    return result


@pipeline_run_object.field("datasetVersions")
def resolve_pipeline_run_dataset_version(run: PipelineRun, info, **kwargs):
    return run.dataset_versions.all()


bindables = [
    pipeline_permissions,
    pipeline_parameter,
    pipeline_object,
    pipeline_run_object,
    pipeline_run_status_enum,
    pipeline_notification_level_enum,
    pipeline_run_order_by_enum,
    pipeline_version_object,
    pipeline_version_permissions,
    generic_output_object,
    pipeline_run_output_union,
]
