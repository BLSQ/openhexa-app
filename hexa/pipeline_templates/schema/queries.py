from ariadne import QueryType

from hexa.pipeline_templates.models import PipelineTemplate

pipeline_template_query = QueryType()


@pipeline_template_query.field("allPipelineTemplates")
def resolve_all_pipeline_templates(_, info):
    return PipelineTemplate.objects.all()


bindables = [
    pipeline_template_query,
]
