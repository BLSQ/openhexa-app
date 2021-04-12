from django.apps import AppConfig
from importlib import import_module


class ConnectorAppConfig(AppConfig):
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
