from ariadne import QueryType
from django.db.models import Q
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.pipeline_templates.models import PipelineTemplate
from hexa.workspaces.models import Workspace

pipeline_template_query = QueryType()


@pipeline_template_query.field("pipelineTemplates")
def resolve_pipeline_templates(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    search = kwargs.get("search", "")

    pipeline_templates = PipelineTemplate.objects.filter(
        Q(name__icontains=search) | Q(description__icontains=search)
    )

    workspace_slug = kwargs.get("workspace_slug")
    if workspace_slug:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
        pipeline_templates = pipeline_templates.filter(workspace=workspace)

    return result_page(
        pipeline_templates,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


@pipeline_template_query.field("templateByCode")
def resolve_template_by_code(_, info, **kwargs):
    try:
        template = PipelineTemplate.objects.get(code=kwargs["code"])
    except PipelineTemplate.DoesNotExist:
        template = None
    return template


bindables = [
    pipeline_template_query,
]
