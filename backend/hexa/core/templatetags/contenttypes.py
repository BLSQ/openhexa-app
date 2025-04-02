from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.filter(name="content_type_key")
def content_type_key(value):
    """Return the natural key of the content type associated with the provided model instance."""
    if value is None or value == "":
        return None

    content_type_key = ContentType.objects.get_for_model(value).natural_key()

    return ".".join(content_type_key)
