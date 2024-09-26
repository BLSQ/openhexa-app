import logging

from ariadne import QueryType
from django.contrib.contenttypes.models import ContentType

from hexa.metadata.schema.utils import get_model_instance

metadata_queries = QueryType()


@metadata_queries.field("metadataAttributes")
def resolve_metadata_query(_, info, **kwargs):
    request = info.context["request"]
    user = request.user
    try:
        model_class, instance = get_model_instance(kwargs.get("opaqueId"))
        if instance.can_view_metadata(user):
            return instance.get_attributes()
    except ContentType.DoesNotExist:
        logging.exception("Content type does not exist")
        return None
    except model_class.DoesNotExist:
        logging.exception("Model does not exist")
        return None


bindables = [metadata_queries]
