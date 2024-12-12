from hexa.app import CoreAppConfig


class TemplatePipelinesConfig(CoreAppConfig):
    name = "hexa.template_pipelines"
    label = "template_pipelines"

    def ready(self):
        from . import signals  # noqa
