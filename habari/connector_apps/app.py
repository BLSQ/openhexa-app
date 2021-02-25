from django.apps import AppConfig, apps


class ConnectorAppConfig(AppConfig):
    @property
    def datasource_type(self):
        """Specify the datasource for which this connector app is relevant. This will allow, among other things, to
        determine what happens when you browse a datasource of a specific type."""
        return None

    @property
    def route_prefix(self):
        """Returns the string prefix to use when including the connector app URLs.
        If your "fooconnector" app defines a "bar" view under the "/bar" URL, setting the prefix to "foo" will make
        the view accessible through "/foo/bar"
        """

        raise NotImplementedError(
            "Each connector app should define a route_prefix() property"
        )

    @property
    def connector_class_name(self):
        raise NotImplementedError(
            f"Each connector app should define a connector_class_name() property"
        )

    @property
    def connector(self):
        return apps.get_model(
            app_label=self.label, model_name=self.connector_class_name
        )
