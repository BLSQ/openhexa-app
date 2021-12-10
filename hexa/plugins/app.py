from importlib import import_module

from django.apps import AppConfig, apps
from django.db.models.base import ModelBase


class ConnectorAppConfig(AppConfig):
    def get_last_activities(self):
        from hexa.core.activities import ActivityList

        return ActivityList()

    @property
    def route_prefix(self):
        """Returns the string prefix to use when including the connector app URLs.
        If your "fooconnector" app defines a "bar" view under the "/bar" URL, setting the prefix to "foo" will make
        the view accessible through "/foo/bar"
        """

        raise NotImplementedError(
            "Each connector app should define a route_prefix() property"
        )

    def get_notebooks_credentials(self):
        """Check if the app config class has a NOTEBOOKS_CREDENTIALS property. This property allows connector plugins to
        provide a list of functions that can update notebooks credentials with plugin-specific credentials."""

        notebooks_credentials_function_paths = getattr(
            self, "NOTEBOOKS_CREDENTIALS", []
        )

        notebooks_credentials_functions = []
        for function_path in notebooks_credentials_function_paths:
            module_name, function_name = function_path.rsplit(".", 1)
            module = import_module(module_name)
            notebooks_credentials_functions.append(getattr(module, function_name))

        return notebooks_credentials_functions

    @classmethod
    def get_models_by_capability(cls, capability, filter_app=None):
        models_by_app: dict[AppConfig, list[ModelBase]] = {}
        for app in apps.get_app_configs():
            if filter_app and app.label != filter_app:
                continue
            if isinstance(app, ConnectorAppConfig):
                models_by_app[app] = []
                for model in app.get_models():
                    if hasattr(model, capability):
                        models_by_app[app].append(model)
        return models_by_app


def get_connector_app_configs():
    """Return the list of Django app configs that corresponds to connector apps"""

    return [
        app for app in apps.get_app_configs() if isinstance(app, ConnectorAppConfig)
    ]
