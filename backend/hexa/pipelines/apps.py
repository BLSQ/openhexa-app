from hexa.app import CoreAppConfig


class PipelinesConfig(CoreAppConfig):
    name = "hexa.pipelines"
    label = "pipelines"

    ANONYMOUS_URLS = [
        "pipelines:credentials",
        "pipelines:run",
        "pipelines:run_with_version",
        # Visitors follow the runs they launched from a public permalink live.
        "pipelines:stream_pipeline_run_messages",
    ]

    def ready(self):
        from . import signals  # noqa
