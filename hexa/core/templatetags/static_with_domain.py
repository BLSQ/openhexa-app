from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(name="static_with_domain")
def static_with_domain(value: str):
    """Returns the static URL with the BASE_URL from the settings.
    Usage:
        {% static_with_domain "path/to/file.png" %}
    """
    static_url = static(value)
    if static_url.startswith("http"):
        return static_url

    return f"{settings.BASE_URL}/{static_url}"
