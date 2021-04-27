from django.utils.formats import date_format as django_date_format

DEFAULT_DATE_FORMAT = "M d, H:i:s (e)"


def date_format(value, format_string=DEFAULT_DATE_FORMAT):
    """Simple wrapper for Django date_format() with a default format."""

    return django_date_format(value, format_string)
