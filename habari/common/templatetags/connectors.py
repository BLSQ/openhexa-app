from django import template

from habari.catalog.connectors import get_connector_app_config

register = template.Library()


@register.simple_tag
def connector_app_label(datasource):
    """Returns the app label"""

    connector_app_config = get_connector_app_config(datasource.datasource_type)

    return connector_app_config.label


@register.simple_tag
def connector_template_dir(datasource):
    """Returns the template dir of a connector app (see connector_apps directory) for the provided datasource"""

    connector_app_config = get_connector_app_config(datasource.datasource_type)

    return f"{connector_app_config.label}/"


@register.simple_tag
def connector_static_dir(datasource):
    """Returns the static dir of a connector app (see connector_apps directory) for the provided datasource"""

    connector_app_config = get_connector_app_config(datasource.datasource_type)

    return f"{connector_app_config.label}/"
