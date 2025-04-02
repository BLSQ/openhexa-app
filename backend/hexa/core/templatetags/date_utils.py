import datetime

from django import template
from django.utils import timezone

from hexa.core.date_utils import DEFAULT_DATE_FORMAT
from hexa.core.date_utils import date_format as core_date_format
from hexa.core.date_utils import duration_format as core_duration_format

register = template.Library()


@register.filter(name="about_now")
def about_now(value, delay=60):
    return value is not None and (timezone.now() - value).seconds < delay


@register.filter(name="date_format")
def date_format(value, format_string=DEFAULT_DATE_FORMAT):
    if value is None or value == "":
        return None

    return core_date_format(value, format_string)


@register.filter(name="duration_format")
def duration_format(value: datetime.timedelta, short_form=False, max_parts: int = 2):
    return core_duration_format(value, short_form=short_form, max_parts=max_parts)
