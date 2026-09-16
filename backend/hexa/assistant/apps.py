import os

import logfire

from hexa.app import CoreAppConfig


class AssistantConfig(CoreAppConfig):
    name = "hexa.assistant"
    label = "assistant"

    def ready(self):
        super().ready()
        if os.environ.get("LOGFIRE_SEND_TO_LOGFIRE", "false").lower() == "true":
            logfire.configure(environment=os.environ.get("SENTRY_ENVIRONMENT"))
            logfire.instrument_pydantic_ai()
