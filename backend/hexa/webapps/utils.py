from django.conf import settings


def extract_webapp_subdomain(hostname):
    """Extract the webapp subdomain from a hostname, or return None if it doesn't match."""
    # Check if subdomain for webapps is enabled
    subdomain_base_url = getattr(settings, "WEBAPPS_SUBDOMAIN_BASE_URL", None)
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
