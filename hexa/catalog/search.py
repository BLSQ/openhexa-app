import stringcase
from django.contrib.contenttypes.models import ContentType

from hexa.catalog.models import CatalogIndex


def perform_search(query, limit=10):
    tokens = query.split(" ")

    try:
        content_type_code = next(t for t in tokens if t[:5] == "type:")[5:]
        other_tokens = [t for t in tokens if t[:5] != "type:"]
        query = " ".join(other_tokens)
        app_code, model_name = content_type_code.split("_", 1)
        app_label = f"connector_{app_code}"
        content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    except StopIteration:
        content_type = None

    return CatalogIndex.objects.search(query, limit=limit, content_type=content_type)
