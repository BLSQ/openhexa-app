from functools import cache
from importlib import import_module

from django.apps import AppConfig, apps
from django.db.models.base import ModelBase


class CoreAppConfig(AppConfig):
    """Base class for our own "core" apps (not connector plugins).

    ANONYMOUS_URLS will be used by our authentication middleware
    (hexa.user_management.middlewares) to authorized anonymous requests to specific URLs or URL prefixes.

    Example:

        class FooConfig(CoreAppConfig):
            name = "hexa.foo"
            label = "foo"

            ANONYMOUS_URLS = ["foo:bar"]
    """

    ANONYMOUS_URLS = []  # URL names (such as "foo:bar")

    def __init_subclass__(cls) -> None:
        """Django does not play super nicely with multiple nested AppConfig subclasses. To make sure that a "concrete"
        app class will be used instead of one of the classes below, we have to make sure that the final subclasses
        have a default property that is set to True.

        TODO: this is a convoluted workaround - consider alternative to AppConfig subclasses for our use case.
        """
        super().__init_subclass__()
        cls.default = True


class ConnectorAppConfig(AppConfig):
    """Base class for connector plugins.

    Example:

        class Dhis2ConnectorConfig(ConnectorAppConfig):
            name = "hexa.plugins.connector_foo"
            label = "connector_foo"

            verbose_name = "Foo Connector"

            NOTEBOOKS_CREDENTIALS = [
                "hexa.plugins.connector_foo.credentials.notebooks_credentials"
            ]

            PIPELINES_CREDENTIALS = [
                "hexa.plugins.connector_foo.credentials.pipelines_credentials"
            ]

            @property
            def route_prefix(self):
                return "foo"
    """

    ANONYMOUS_URLS = []  # URL names (such as "foo:bar")
    NOTEBOOKS_CREDENTIALS = []
    PIPELINES_CREDENTIALS = []

    def __init_subclass__(cls) -> None:
        """Django does not play super nicely with multiple nested AppConfig subclasses. To make sure that a "concrete"
        app class will be used instead of one of the classes below, we have to make sure that the final subclasses
        have a default property that is set to True.

        TODO: this is a convoluted workaround - consider alternative to AppConfig subclasses for our use case.
        """
        super().__init_subclass__()
        cls.default = True

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
        provide a list of functions that can update notebooks credentials with plugin-specific credentials.
        """
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
        provide a list of functions that can update pipelines credentials with plugin-specific credentials.
        """
        pipelines_credentials_function_paths = getattr(
            self, "PIPELINES_CREDENTIALS", []
        )

        pipelines_credentials_functions = []
        for function_path in pipelines_credentials_function_paths:
            module_name, function_name = function_path.rsplit(".", 1)
            module = import_module(module_name)
            pipelines_credentials_functions.append(getattr(module, function_name))

        return pipelines_credentials_functions


@cache
def get_hexa_app_configs(connector_only=False):
    """Return the list of Django app configs that corresponds to our own hexa apps.

    You may use connector_only=True to only fetch connector plugins.
    """
    matched_classes = (
        (ConnectorAppConfig,) if connector_only else (CoreAppConfig, ConnectorAppConfig)
    )

    return [app for app in apps.get_app_configs() if isinstance(app, matched_classes)]


@cache
def get_hexa_models_by_capability(capability: str, filter_app: str = None):
    """Return a dictionary of models that have the requested capability, grouped by app."""
    models_by_app: dict[AppConfig, list[ModelBase]] = {}
    for app in get_hexa_app_configs(connector_only=True):
        if filter_app and app.label != filter_app:
            continue
        models_by_app[app] = []
        for model in app.get_models():
            if hasattr(model, capability):
                models_by_app[app].append(model)

    return models_by_app
