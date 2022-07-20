from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class PipelinesConfig(AppConfig, CoreAppConfig):
    name = "hexa.pipelines"
    label = "pipelines"

    ANONYMOUS_URLS = ["pipelines:credentials"]
