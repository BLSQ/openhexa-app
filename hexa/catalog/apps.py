from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class CatalogConfig(AppConfig, CoreAppConfig):
    name = "hexa.catalog"
    label = "catalog"
