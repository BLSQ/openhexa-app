from urllib.parse import urlencode

from django.conf import settings

POWERED_BY_TARGET_URL = "https://www.openhexa.com/"


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
