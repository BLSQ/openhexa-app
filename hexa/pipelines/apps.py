from django.apps import AppConfig


class PipelinesConfig(AppConfig):
    name = "hexa.pipelines"
    label = "pipelines"

    ANONYMOUS_URLS = ["pipelines:credentials"]
