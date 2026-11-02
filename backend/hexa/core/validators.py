import re

from django.core.exceptions import ValidationError


def validate_public_slug(value):
    if len(value) > 255 or not _PUBLIC_SLUG_RE.match(value):
        raise ValidationError(
            "Public slug must be lowercase alphanumeric words separated by single "
            "hyphens, and 255 characters or fewer.",
            code="PUBLIC_SLUG_INVALID_FORMAT",
        )
    if value in RESERVED_PUBLIC_SLUGS:
        raise ValidationError(
            "This public slug is reserved.", code="PUBLIC_SLUG_RESERVED"
        )


_BLSQ_SPECIFIC = {"snt", "dhis2", "nmdr", "iaso", "openhexa"}

_DNS_AND_NETWORKING = {
    "ns1",
    "ns2",
    "ns3",
    "ns4",
    "mx",
    "dns",
    "ntp",
    "proxy",
    "vpn",
    "cdn",
    "gateway",
    "ingress",
}

_EMAIL = {
    "mail",
    "smtp",
    "pop",
    "imap",
    "webmail",
    "email",
    "postmaster",
    "abuse",
    "noreply",
    "autoconfig",
    "autodiscover",
}

_AUTH = {"auth", "login", "sso", "oauth", "account", "accounts"}

_ENVIRONMENTS = {
    "dev",
    "staging",
    "test",
    "beta",
    "demo",
    "sandbox",
    "localhost",
    "prod",
    "production",
    "preview",
    "canary",
}

_INFRASTRUCTURE_SERVICES = {
    "git",
    "ssh",
    "sftp",
    "ftp",
    "ldap",
    "registry",
    "minio",
    "storage",
    "backup",
    "cache",
}

_MONITORING_AND_OBSERVABILITY = {
    "status",
    "health",
    "monitoring",
    "grafana",
    "prometheus",
    "alertmanager",
    "kibana",
    "elasticsearch",
    "sentry",
    "jaeger",
    "metrics",
    "analytics",
    "telemetry",
    "logs",
}

_CI_CD = {"ci", "cd", "jenkins", "gitlab", "argocd", "deploy"}

_DATABASES_AND_MESSAGING = {
    "db",
    "database",
    "mysql",
    "postgres",
    "redis",
    "mongo",
    "rabbitmq",
    "kafka",
}

_WEB_AND_APP = {
    "www",
    "api",
    "admin",
    "app",
    "static",
    "assets",
    "media",
    "docs",
    "help",
    "support",
    "blog",
    "dashboard",
    "console",
    "portal",
    "intranet",
    "internal",
    "wiki",
}

_SECURITY = {"wpad", "vault", "certs", "security"}

# Kept free so they can become fixed routes next to /<resource>/<public_slug> without
# shadowing an existing permalink.
_ROUTES = {"new", "search", "create", "edit", "settings"}

RESERVED_PUBLIC_SLUGS = (
    _BLSQ_SPECIFIC
    | _DNS_AND_NETWORKING
    | _EMAIL
    | _AUTH
    | _ENVIRONMENTS
    | _INFRASTRUCTURE_SERVICES
    | _MONITORING_AND_OBSERVABILITY
    | _CI_CD
    | _DATABASES_AND_MESSAGING
    | _WEB_AND_APP
    | _SECURITY
    | _ROUTES
)

_PUBLIC_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
