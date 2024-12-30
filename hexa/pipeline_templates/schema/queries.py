from ariadne import QueryType

from hexa.core.graphql import result_page
from hexa.pipeline_templates.models import PipelineTemplate

pipeline_template_query = QueryType()


@pipeline_template_query.field("pipelineTemplates")
def resolve_pipeline_templates(_, info, **kwargs):
    search = kwargs.get("search", "")
    pipeline_templates = PipelineTemplate.objects.filter(name__icontains=search)

    return result_page(
        pipeline_templates,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


bindables = [
    pipeline_template_query,
]
