import stringcase
from django.contrib.contenttypes.models import ContentType

from habari.catalog.models import CatalogIndex


def perform_search(query, limit=10):
    tokens = query.split(" ")

    try:
        model_code = next(t for t in tokens if t[:5] == "type:")[5:]
        other_tokens = [t for t in tokens if t[:5] != "type:"]
        query = " ".join(other_tokens)
        app_label, _ = model_code.split("_", 1)
        model_name = stringcase.camelcase(f"{model_code}")
        content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    except StopIteration:
        content_type = None

    return CatalogIndex.objects.search(query, limit=limit, content_type=content_type)
