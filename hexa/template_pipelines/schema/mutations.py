from ariadne import MutationType
from django.http import HttpRequest

from hexa.analytics.api import track
from hexa.pipelines.models import (
    Pipeline,
    PipelineType,
)
from hexa.workspaces.models import Workspace

template_pipelines_mutations = MutationType()


@template_pipelines_mutations.field("createTemplate")
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

    data = {
        "code": input["code"],
        "name": input.get("name"),
        "workspace": workspace,
    }
    pipeline = Pipeline.objects.create(**data)
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

    return {"pipeline": pipeline, "success": True, "errors": []}


bindables = [template_pipelines_mutations]
