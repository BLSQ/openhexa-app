from django import template as django_template

from hexa.core.models import WithStatus

register = django_template.Library()

STATUS_MAPPINGS = {
    WithStatus.UNKNOWN: "gray",
    WithStatus.SUCCESS: "green",
    WithStatus.ERROR: "red",
    WithStatus.PENDING: "yellow",
}


@register.filter(name="status_color")
def status_color(value):
    try:
        return STATUS_MAPPINGS[value.hexa_status]
    except AttributeError:
        return STATUS_MAPPINGS[WithStatus.UNKNOWN]
