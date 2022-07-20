from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class TagsConfig(AppConfig, CoreAppConfig):
    name = "hexa.tags"
    label = "tags"
