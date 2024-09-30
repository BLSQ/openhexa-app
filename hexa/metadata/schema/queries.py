import logging

from ariadne import QueryType
from django.contrib.contenttypes.models import ContentType

metadata_queries = QueryType()


@metadata_queries.field("metadataAttributes")
def resolve_metadata_query(_, info, **kwargs):
    request = info.context["request"]
    user = request.user
    try:
        model_instance = kwargs.get("opaqueId")
        if model_instance.can_view_metadata(user):
            return model_instance.get_attributes()
    except ContentType.DoesNotExist:
        logging.exception("Content type does not exist")
        return None


bindables = [metadata_queries]
