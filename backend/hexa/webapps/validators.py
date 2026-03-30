from django.core.exceptions import ValidationError
from django.core.validators import DomainNameValidator

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

RESERVED_SUBDOMAINS = (
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
)

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
            "Subdomain must be at least 3 characters.", code="subdomain_too_short"
        )
    if "." in value:
        raise ValidationError(
            "Subdomain must be a single DNS label (no dots).",
            code="subdomain_has_dots",
        )
    if value in RESERVED_SUBDOMAINS:
        raise ValidationError("This subdomain is reserved.", code="subdomain_reserved")
    try:
        _domain_validator(f"{value}.com")
    except ValidationError:
        raise ValidationError(
            "Subdomain must be alphanumeric with hyphens, no leading/trailing hyphens, "
            "and 63 characters or fewer.",
            code="subdomain_invalid_format",
        )
