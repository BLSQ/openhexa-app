from ariadne import MutationType
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from hexa.analytics.api import track
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.template_pipelines.models import Template
from hexa.workspaces.models import Workspace

template_pipelines_mutations = MutationType()


@template_pipelines_mutations.field("createTemplateVersion")
def resolve_create_template(_, info, **kwargs):
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
    if not request.user.has_perm("templates.create_template", workspace):
        raise PermissionDenied()
    try:
        source_pipeline = Pipeline.objects.filter_for_user(request.user).get(
            id=input.get("pipeline_id")
        )
    except Pipeline.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_NOT_FOUND"],
        }
    try:
        source_pipeline_version = source_pipeline.versions.get(
            version_number=input.get("pipeline_version_id")
        )
    except PipelineVersion.DoesNotExist:
        return {
            "success": False,
            "errors": ["PIPELINE_VERSION_NOT_FOUND"],
        }

    template = (
        source_pipeline.template
        if source_pipeline.template
        else Template.objects.create(
            name=input.get("name"),
            code=input.get("code"),
            description=input.get("description"),
            config=input.get("config"),
            workspace=workspace,
            source_pipeline=source_pipeline,
        )
    )
    source_pipeline.template = template
    source_pipeline.save()
    template.create_version(source_pipeline_version=source_pipeline_version)
    track(
        request,
        "templates.template_created",
        {
            "template_id": str(template.id),
            "workspace": workspace.slug,
        },
    )
    return {"template": template, "success": True, "errors": []}


bindables = [template_pipelines_mutations]
