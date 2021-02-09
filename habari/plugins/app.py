from django.apps import AppConfig


class HabariPluginAppConfig(AppConfig):
    @staticmethod
    def get_datasource_types():
        return {}
