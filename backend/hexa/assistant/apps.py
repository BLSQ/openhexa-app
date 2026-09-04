import os

import logfire

from hexa.app import CoreAppConfig


class AssistantConfig(CoreAppConfig):
    name = "hexa.assistant"
    label = "assistant"

    def ready(self):
        super().ready()
        # Imported here rather than at module level: pulling the agents in at
        # import time would load the instruction docs before the app registry
        # is ready.
        from hexa.assistant.agents import pinnable_agent_keys
        from hexa.assistant.model_selection import warn_on_unknown_overrides

        warn_on_unknown_overrides(pinnable_agent_keys())

        if os.environ.get("LOGFIRE_SEND_TO_LOGFIRE", "false").lower() == "true":
            logfire.configure(environment=os.environ.get("SENTRY_ENVIRONMENT"))
            logfire.instrument_pydantic_ai()
