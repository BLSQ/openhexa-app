from hexa.assistant.agents.agent import AssistantAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.mcp.tools import create_pipeline as mcp_create_pipeline
from hexa.pipelines.models import PipelineFunctionalType


class PipelineAgent(AssistantAgent):
    instruction_set = InstructionSet.PIPELINE

    def _get_tools(self, conversation: Conversation) -> list:
        user = conversation.user
        workspace_slug = conversation.workspace.slug

        def create_pipeline(
            name: str,
            source_code: str,
            description: str = "",
            functional_type: PipelineFunctionalType | None = None,
        ) -> dict:
            return mcp_create_pipeline(
                user=user,
                workspace_slug=workspace_slug,
                name=name,
                source_code=source_code,
                description=description,
                functional_type=functional_type,
            )

        create_pipeline.__doc__ = mcp_create_pipeline.__doc__

        return [create_pipeline]
