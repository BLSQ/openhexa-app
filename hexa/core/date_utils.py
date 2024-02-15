import datetime

from django.utils.formats import date_format as django_date_format
from django.utils.translation import gettext, ngettext

DEFAULT_DATE_FORMAT = "M d, H:i:s (e)"
ONE_HOUR = 60 * 60
ONE_MINUTE = 60


def date_format(value: datetime.datetime, format_string=DEFAULT_DATE_FORMAT):
    """Simple wrapper for Django date_format() with a default format."""
    return django_date_format(value, format_string)


def duration_format(value: datetime.timedelta, *, short_form=False, max_parts: int = 2):
    """Convert timedelta to x hours, x minutes-style strings"""
    parts = []
    display_seconds = True
    full_hours = value.seconds // ONE_HOUR
    full_minutes = value.seconds % ONE_HOUR // ONE_MINUTE
    full_seconds = value.seconds % ONE_MINUTE

    if full_hours > 0:
        display_seconds = False
        parts.append(
            ngettext(
                "%(hours)d hour",
                "%(hours)d hours",
                full_hours,
            )
            % {
                "hours": full_hours,
            }
            if not short_form
            else gettext("%dh" % full_hours)
        )
    if full_minutes > 0:
        parts.append(
            ngettext(
                "%(minutes)d minute",
                "%(minutes)d minutes",
                full_minutes,
            )
            % {
                "minutes": full_minutes,
            }
            if not short_form
            else gettext("%dm" % full_minutes)
        )
    if display_seconds and full_seconds > 0:
        parts.append(
            ngettext(
                "%(seconds)d second",
                "%(seconds)d seconds",
                full_seconds,
            )
            % {
                "seconds": full_seconds,
            }
            if not short_form
            else gettext("%ds" % full_seconds)
        )

    return (", " if not short_form else " ").join(parts[:max_parts])
