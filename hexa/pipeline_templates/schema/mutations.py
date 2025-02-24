from ariadne import MutationType
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest

from hexa.analytics.api import track
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

pipeline_template_mutations = MutationType()


def get_workspace(user: User, workspace_slug: str) -> Workspace | None:
    try:
        return Workspace.objects.filter_for_user(user).get(slug=workspace_slug)
    except Workspace.DoesNotExist:
        return None


def get_source_pipeline(user: User, pipeline_id: str) -> Pipeline | None:
    """
    Get a pipeline that the user has access to, regardless of whether it has been deleted or not.
    """
    try:
        return Pipeline.all_objects.filter_for_user(user).get(id=pipeline_id)
    except Pipeline.DoesNotExist:
        return None


def get_source_pipeline_version(
    source_pipeline: Pipeline, pipeline_version_id: str
) -> PipelineVersion | None:
    try:
        return source_pipeline.versions.get(id=pipeline_version_id)
    except PipelineVersion.DoesNotExist:
        return None


@pipeline_template_mutations.field("createPipelineTemplateVersion")
def resolve_create_pipeline_template_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    workspace = get_workspace(request.user, input.get("workspace_slug"))
    if not workspace:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}

    if not request.user.has_perm(
        "pipeline_templates.create_pipeline_template_version", workspace
    ):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    source_pipeline = get_source_pipeline(request.user, input["pipeline_id"])
    if not source_pipeline:
        return {"success": False, "errors": ["PIPELINE_NOT_FOUND"]}

    source_pipeline_version = get_source_pipeline_version(
        source_pipeline, input.get("pipeline_version_id")
    )
    if not source_pipeline_version:
        return {"success": False, "errors": ["PIPELINE_VERSION_NOT_FOUND"]}

    try:
        pipeline_template, template_created = source_pipeline.get_or_create_template(
            name=input.get("name"),
            code=input.get("code"),
            description=input.get("description"),
        )
        pipeline_template_version = (
            source_pipeline_version.template_version
            if hasattr(source_pipeline_version, "template_version")
            else pipeline_template.create_version(
                source_pipeline_version,
                user=request.user,
                changelog=input.get("changelog"),
            )
        )  # Recreate the version if the source pipeline version has no template version (it can have one if the template was deleted before and restored)
    except IntegrityError as e:
        if any(
            msg in str(e)
            for msg in [
                "unique_template_code_per_workspace",
                "unique_template_name",
            ]
        ):
            return {"success": False, "errors": ["DUPLICATE_TEMPLATE_NAME_OR_CODE"]}
        return {"success": False, "errors": ["UNKNOWN_ERROR"]}

    track(
        request,
        "pipeline_templates.pipeline_template_created"
        if template_created
        else "pipeline_templates.pipeline_template_updated",
        {
            "pipeline_template_id": str(pipeline_template.id),
            "pipeline_template_version_id": str(pipeline_template_version.id),
            "workspace": workspace.slug,
        },
    )
    return {"pipeline_template": pipeline_template, "success": True, "errors": []}


@pipeline_template_mutations.field("updateTemplateVersion")
def resolve_update_template_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        template_version = PipelineTemplateVersion.objects.filter_for_user(
            request.user
        ).get(id=input.pop("id"))
        template_version.update_if_has_perm(request.user, **input)
        return {"template_version": template_version, "success": True, "errors": []}
    except PipelineTemplateVersion.DoesNotExist:
        return {
            "success": False,
            "errors": ["NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }


@pipeline_template_mutations.field("deleteTemplateVersion")
def resolve_delete_template_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        PipelineTemplateVersion.objects.get(id=input["id"]).delete_if_has_perm(
            request.user
        )
        return {
            "success": True,
            "errors": [],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except PipelineTemplateVersion.DoesNotExist:
        return {
            "success": False,
            "errors": ["TEMPLATE_VERSION_NOT_FOUND"],
        }


@pipeline_template_mutations.field("createPipelineFromTemplateVersion")
def resolve_create_pipeline_from_template_version(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    user = request.user
    input = kwargs["input"]

    workspace = get_workspace(user, input.get("workspace_slug"))
    if not workspace:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}

    if not user.has_perm("pipelines.create_pipeline", workspace):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    try:
        template_version = PipelineTemplateVersion.objects.get(
            id=input["pipeline_template_version_id"]
        )
    except PipelineTemplateVersion.DoesNotExist:
        return {"success": False, "errors": ["PIPELINE_TEMPLATE_VERSION_NOT_FOUND"]}

    pipeline_version = template_version.create_pipeline_version(user, workspace)

    track(
        request,
        "pipeline_templates.pipeline_template_used",
        {
            "pipeline_id": str(pipeline_version.pipeline.id),
            "pipeline_version_id": str(pipeline_version.id),
            "pipeline_template_id": str(template_version.template.id),
            "pipeline_template_version_id": str(template_version.id),
            "workspace": workspace.slug,
        },
    )
    return {"pipeline": pipeline_version.pipeline, "success": True, "errors": []}


@pipeline_template_mutations.field("updatePipelineTemplate")
def resolve_update_template(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        template = PipelineTemplate.objects.filter_for_user(request.user).get(
            id=input.pop("id")
        )
        template.update_if_has_perm(request.user, **input)
        return {"template": template, "success": True, "errors": []}
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except PipelineTemplate.DoesNotExist:
        return {
            "success": False,
            "errors": ["NOT_FOUND"],
        }


@pipeline_template_mutations.field("deletePipelineTemplate")
def resolve_delete_pipeline_template(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        pipeline_template = PipelineTemplate.objects.filter_for_user(
            user=request.user
        ).get(id=input.get("id"))
        pipeline_template.delete_if_has_perm(principal=request.user)
        return {
            "success": True,
            "errors": [],
        }
    except PipelineTemplate.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_TEMPLATE_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }


bindables = [pipeline_template_mutations]
