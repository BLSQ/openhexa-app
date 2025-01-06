from hexa.app import CoreAppConfig


class ConnectionsConfig(CoreAppConfig):
    name = "hexa.connections"
    label = "connections"

    ANONYMOUS_URLS = ["connections:credentials"]
