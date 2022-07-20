from importlib import import_module

from django.apps import AppConfig, apps
from django.db.models.base import ModelBase
from django.http import HttpRequest


class CoreAppConfig:
    ANONYMOUS_URLS = []
    ANONYMOUS_PREFIXES = []


class ConnectorAppConfig(CoreAppConfig):
    NOTEBOOKS_CREDENTIALS = []
    PIPELINES_CREDENTIALS = []
    LAST_ACTIVITIES = None
    EXTRA_GRAPHQL_ME_AUTHORIZED_ACTIONS_RESOLVER = None

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

    def get_pipelines_credentials(self):
        """Check if the app config class has a PIPELINES_CREDENTIALS property. This property allows connector plugins to
        provide a list of functions that can update pipelines credentials with plugin-specific credentials."""

        pipelines_credentials_function_paths = getattr(
            self, "PIPELINES_CREDENTIALS", []
        )

        pipelines_credentials_functions = []
        for function_path in pipelines_credentials_function_paths:
            module_name, function_name = function_path.rsplit(".", 1)
            module = import_module(module_name)
            pipelines_credentials_functions.append(getattr(module, function_name))

        return pipelines_credentials_functions

    def get_last_activities(self, request: HttpRequest):
        """Check if the app config class has a LAST_ACTIVITIES property. This property allows connector plugins to
        provide a function path. The function will be called by the core module to gather activities across plugins."""

        last_activity_function_path = getattr(self, "LAST_ACTIVITIES", None)

        if last_activity_function_path is not None:
            module_name, function_name = last_activity_function_path.rsplit(".", 1)
            module = import_module(module_name)
            return getattr(module, function_name)(request)

        # Cannot import this module beforehand - Django will complain about apps not being initialized yet
        from hexa.core.activities import ActivityList

        return ActivityList()

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

    def get_extra_graphql_me_authorized_actions_resolver(self):
        """Check if this app has an extra resolver for the "authorizedActions" field on the "Me" type.
        The base resolver will loop through all plugins and extend the authorized actions list with any extra
        resolver found.
        """

        if self.EXTRA_GRAPHQL_ME_AUTHORIZED_ACTIONS_RESOLVER is None:
            return None

        (
            module_name,
            function_name,
        ) = self.EXTRA_GRAPHQL_ME_AUTHORIZED_ACTIONS_RESOLVER.rsplit(".", 1)
        schema_module = import_module(module_name)
        extra_resolver = getattr(schema_module, function_name)

        if not callable(extra_resolver):
            raise TypeError(
                f"{self.EXTRA_GRAPHQL_ME_AUTHORIZED_ACTIONS_RESOLVER} is not callable"
            )

        return extra_resolver


def get_hexa_app_configs(connector_only=False):
    """Return the list of Django app configs that corresponds to connector apps"""

    return [
        app
        for app in apps.get_app_configs()
        if isinstance(app, ConnectorAppConfig if connector_only else CoreAppConfig)
    ]
