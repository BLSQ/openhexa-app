from hexa.app import ConnectorAppConfig


class PostgresqlConnectorConfig(ConnectorAppConfig):
    name = "hexa.plugins.connector_postgresql"
    label = "connector_postgresql"

    verbose_name = "Postgresql Connector"

    NOTEBOOKS_CREDENTIALS = [
        "hexa.plugins.connector_postgresql.credentials.notebooks_credentials"
    ]

    PIPELINES_CREDENTIALS = [
        "hexa.plugins.connector_postgresql.credentials.pipelines_credentials"
    ]
