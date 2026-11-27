import re

from django.core.exceptions import ValidationError


def validate_public_slug(value):
    if len(value) > 255 or not _PUBLIC_SLUG_RE.match(value):
        raise ValidationError(
            "Public slug must be lowercase letters and numbers, separated by single "
            "hyphens or underscores, and 255 characters or fewer.",
            code="PUBLIC_SLUG_INVALID_FORMAT",
        )
    if value in RESERVED_PUBLIC_SLUGS:
        raise ValidationError(
            "This public slug is reserved.", code="PUBLIC_SLUG_RESERVED"
        )


# Public slugs only ever appear as a path segment, as in /<resource>/<public_slug>.
# These are kept free so they can become fixed routes next to it without shadowing
# an existing permalink.
RESERVED_PUBLIC_SLUGS = {
    "new",
    "search",
    "create",
    "edit",
    "settings",
    "api",
    "admin",
    "static",
    "assets",
    "media",
    "public",
    "explore",
    "embed",
    "download",
    "export",
}

_PUBLIC_SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
