from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class NotebooksConfig(AppConfig, CoreAppConfig):
    name = "hexa.notebooks"
    label = "notebooks"
