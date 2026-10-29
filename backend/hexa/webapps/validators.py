from django.core.exceptions import ValidationError
from django.core.validators import DomainNameValidator

from hexa.core.validators import RESERVED_PUBLIC_SLUGS
from hexa.webapps.utils import PREVIEW_KEY_RE

# This validates for:
# RFC 1034 DNS label rules (max 63 chars, valid characters, no leading/trailing hyphens).
# A little trick: We append ".com" to the subdomain and validate as a full domain
# to leverage Django's implementation.
_domain_validator = DomainNameValidator(accept_idna=False)


def validate_subdomain(value):
    if value != value.lower():
        raise ValidationError(
            "Subdomain must be lowercase.", code="SUBDOMAIN_NOT_LOWERCASE"
        )
    if len(value) < 3:
        raise ValidationError(
            "Subdomain must be at least 3 characters.", code="SUBDOMAIN_TOO_SHORT"
        )
    if "." in value:
        raise ValidationError(
            "Subdomain must be a single DNS label (no dots).",
            code="SUBDOMAIN_HAS_DOTS",
        )
    if value in RESERVED_PUBLIC_SLUGS or PREVIEW_KEY_RE.match(value):
        raise ValidationError("This subdomain is reserved.", code="SUBDOMAIN_RESERVED")
    try:
        _domain_validator(f"{value}.com")
    except ValidationError:
        raise ValidationError(
            "Subdomain must be alphanumeric with hyphens, no leading/trailing hyphens, "
            "and 63 characters or fewer.",
            code="SUBDOMAIN_INVALID_FORMAT",
        )
