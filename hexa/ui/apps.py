from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class UiConfig(AppConfig, CoreAppConfig):
    name = "hexa.ui"
    label = "ui"

    verbose_name = "UI"
