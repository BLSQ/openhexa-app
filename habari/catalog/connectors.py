from django.apps import apps

from habari.connector_apps.app import ConnectorAppConfig


def get_connector_app_configs():
    """Return the list of Django app configs that corresponds to connector apps"""

    return [
        app for app in apps.get_app_configs() if isinstance(app, ConnectorAppConfig)
    ]


def get_connector_app_config(datasource):
    """Find the connector app config associated with a specific datasource type"""

    try:
        return next(
            app_config
            for app_config in get_connector_app_configs()
            if app_config.datasource_type == datasource.datasource_type
        )
    except StopIteration:
        return None
