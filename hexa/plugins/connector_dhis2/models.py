from logging import getLogger

from django.core.exceptions import ValidationError

logger = getLogger(__name__)


def validate_dhis2_base_url(value):
    if value.endswith("/"):
        raise ValidationError("DHIS2 url should not end with a '/'")
