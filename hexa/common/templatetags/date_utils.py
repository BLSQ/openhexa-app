from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name="about_now")
def about_now(value, delay=60):
    return value is not None and (timezone.now() - value).seconds < delay
