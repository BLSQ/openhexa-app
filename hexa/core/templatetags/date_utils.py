from django import template
from django.utils import timezone

from hexa.core.date_utils import DEFAULT_DATE_FORMAT
from hexa.core.date_utils import date_format as core_date_format

register = template.Library()


@register.filter(name="about_now")
def about_now(value, delay=60):
    return value is not None and (timezone.now() - value).seconds < delay


@register.filter(name="date_format")
def date_format(value, format_string=DEFAULT_DATE_FORMAT):
    if value is None or value == "":
        return None

    return core_date_format(value, format_string)
