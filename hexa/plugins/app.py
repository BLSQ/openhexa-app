from django.apps import AppConfig


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
