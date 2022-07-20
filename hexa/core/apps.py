from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class CoreConfig(AppConfig, CoreAppConfig):
    name = "hexa.core"
    label = "core"
