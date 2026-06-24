from django.core.management.base import BaseCommand

from hexa.assistant.agents import (
    AGENT_TOOLS_SCHEMA_PATH,
    render_agent_tools_schema,
)


class Command(BaseCommand):
    help = (
        "Regenerate the AssistantToolName GraphQL enum from the live agent "
        "registry. Run this after adding, removing, or renaming a tool on any "
        "agent, then run `npm run codegen` in the frontend."
    )

    def handle(self, *args, **options):
        AGENT_TOOLS_SCHEMA_PATH.write_text(render_agent_tools_schema())
        self.stdout.write(self.style.SUCCESS(f"Wrote {AGENT_TOOLS_SCHEMA_PATH.name}"))
