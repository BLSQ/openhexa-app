from ariadne import MutationType
from django.http import HttpRequest

from hexa.analytics.api import track
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.workspaces.models import Workspace

pipeline_template_mutations = MutationType()


def get_workspace(user, workspace_slug):
    try:
        return Workspace.objects.filter_for_user(user).get(slug=workspace_slug)
    except Workspace.DoesNotExist:
        return None


def get_source_pipeline(user, pipeline_id):
    try:
        return Pipeline.objects.filter_for_user(user).get(id=pipeline_id)
    except Pipeline.DoesNotExist:
        return None


def get_source_pipeline_version(source_pipeline, pipeline_version_id):
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

    source_pipeline = get_source_pipeline(request.user, input.get("pipeline_id"))
    if not source_pipeline:
        return {"success": False, "errors": ["PIPELINE_NOT_FOUND"]}

    source_pipeline_version = get_source_pipeline_version(
        source_pipeline, input.get("pipeline_version_id")
    )
    if not source_pipeline_version:
        return {"success": False, "errors": ["PIPELINE_VERSION_NOT_FOUND"]}

    pipeline_template = source_pipeline.get_or_create_template(
        name=input.get("name"),
        code=input.get("code"),
        description=input.get("description"),
        config=input.get("config"),
    )
    pipeline_template_version = pipeline_template.create_version(
        source_pipeline_version
    )
    track(
        request,
        "pipeline_templates.pipeline_template_created",
        {
            "pipeline_template_id": str(pipeline_template.id),
            "pipeline_template_version_id": str(pipeline_template_version.id),
            "workspace": workspace.slug,
        },
    )
    return {"pipeline_template": pipeline_template, "success": True, "errors": []}


bindables = [pipeline_template_mutations]
