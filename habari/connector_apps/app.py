from django.apps import AppConfig


class ConnectorAppConfig(AppConfig):
    @property
    def datasource_type(self):
        return None
