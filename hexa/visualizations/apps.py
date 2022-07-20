from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class VisualizationsConfig(AppConfig, CoreAppConfig):
    name = "hexa.visualizations"
    label = "visualizations"
