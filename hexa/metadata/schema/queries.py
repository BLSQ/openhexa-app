from ariadne import QueryType

metadata_queries = QueryType()


@metadata_queries.field("metadataAttributes")
def resolve_metadata_query(_, info, **kwargs):
    request = info.context["request"]
    user = request.user
    model_instance = kwargs.get("target_id")
    if model_instance.can_view_metadata(user):
        return model_instance.attributes.all()


bindables = [metadata_queries]
