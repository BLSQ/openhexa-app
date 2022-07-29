from hexa.app import CoreAppConfig


class PipelinesConfig(CoreAppConfig):
    name = "hexa.pipelines"
    label = "pipelines"

    ANONYMOUS_URLS = ["pipelines:credentials"]
