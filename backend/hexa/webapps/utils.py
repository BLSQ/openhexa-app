import re
from urllib.parse import urlencode, urlparse

from django.conf import settings

PREVIEW_KEY_RE = re.compile(r"^[a-z0-9]{32}$")
POWERED_BY_TARGET_URL = "https://www.openhexa.com/"


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


def webapp_host_url(label):
    """Base URL for a webapp host, built from its first DNS label — either the
    webapp's subdomain (serve URL) or a preview session key (preview URL).
    """
    return f"{settings.SCHEME}://{label}.{settings.WEBAPPS_DOMAIN}/"


def powered_by_url(request, source):
    """Build the marketing-site link for a 'Powered by OpenHEXA' banner, tagged
    with UTM parameters so Google Analytics on openhexa.com can attribute traffic.

    UTM scheme: a constant `utm_source` groups all banner traffic under a single
    source, `utm_content` carries the surface (iFrame, Static, Superset), and
    `utm_term` carries the serving host so per-deployment/custom-domain detail is
    preserved separately.
    """
    query = urlencode(
        {
            "utm_source": "openhexa-webapps",
            "utm_medium": "referral",
            "utm_campaign": "powered-by-openhexa-banner",
            "utm_content": source,
            "utm_term": request.get_host(),
        }
    )
    return f"{POWERED_BY_TARGET_URL}?{query}"


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
