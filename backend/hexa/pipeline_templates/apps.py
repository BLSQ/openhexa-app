from hexa.app import CoreAppConfig


class PipelineTemplatesConfig(CoreAppConfig):
    name = "hexa.pipeline_templates"
    label = "pipeline_templates"

    def ready(self):
        super().ready()
        import hexa.pipeline_templates.signals  # noqa
