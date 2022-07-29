from hexa.app import ConnectorAppConfig


class AccessmodConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_accessmod"
    label = "connector_accessmod"

    verbose_name = "Accessmod Connector"

    ANONYMOUS_URLS = ["connector_accessmod:webhook"]
    EXTRA_GRAPHQL_ME_AUTHORIZED_ACTIONS_RESOLVER = (
        "hexa.plugins.connector_accessmod.schema.extra_resolve_me_authorized_actions"
    )

    @property
    def route_prefix(self):
        return "accessmod"

    def ready(self):
        from . import signals  # noqa
