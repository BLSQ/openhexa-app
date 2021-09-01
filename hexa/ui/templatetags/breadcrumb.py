from django import template
from django.urls import reverse

register = template.Library()


@register.filter(name="as_url")
def as_url(breadcrumb):
    if len(breadcrumb) < 2:
        return ""
    text, name, *args = breadcrumb
    return reverse(name, args=args)
