import re
from urllib.parse import urlparse

from django.conf import settings

PREVIEW_KEY_RE = re.compile(r"^[a-z0-9]{32}$")


def is_local_dev_origin(origin):
    """Whether an Origin header value denotes a local development context."""
    if not origin:
        return False
    if origin == "null":
        return True
    parsed = urlparse(origin)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {
        "localhost",
        "127.0.0.1",
        "::1",
    }


def is_preview_host(host):
    """Whether a request host is a preview URL."""
    label = extract_webapp_subdomain(host)
    return bool(label and PREVIEW_KEY_RE.match(label))


def extract_webapp_subdomain(hostname):
    """Extract the webapp subdomain from a hostname, or return None if it doesn't match."""
    # Check if subdomain for webapps is enabled
    subdomain_base_url = getattr(settings, "WEBAPPS_DOMAIN", None)
    if not subdomain_base_url:
        return None

    # Remove port if any (for example for local testing)
    subdomain_base = subdomain_base_url.split(":")[0]
    hostname = hostname.split(":")[0]

    # Check if we're calling a valid webapps subdomain
    if not hostname.endswith(f".{subdomain_base}"):
        return None
    subdomain = hostname.removesuffix(f".{subdomain_base}")
    if not subdomain or "." in subdomain:
        return None

    return subdomain
