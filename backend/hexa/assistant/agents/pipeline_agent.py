from hexa.assistant.agents.agent import AssistantAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.pipelines.models import PipelineFunctionalType


class PipelineAgent(AssistantAgent):
    instruction_set = InstructionSet.PIPELINE

    def _get_tools(self, conversation: Conversation) -> list:
        # Lazy import to avoid circular dependency
        from hexa.mcp.tools import create_pipeline as mcp_create_pipeline
        from hexa.mcp.tools import (
            create_pipeline_version as mcp_create_pipeline_version,
        )

        user = conversation.user
        workspace_slug = conversation.workspace.slug

        def create_pipeline(
            name: str,
            description: str = "",
            functional_type: PipelineFunctionalType | None = None,
        ) -> dict:
            """Create a new pipeline in the current workspace. Returns the pipeline id, code, and name.

            Always provide a meaningful description summarizing what the pipeline does.
            If the pipeline has no clear purpose or is blank, use "" as the description.
            Only the fields name, description, and functional_type are supported at creation time.
            Fields such as schedule, timeout, tags, or webhook settings cannot be set here.
            """
            return mcp_create_pipeline(
                user=user,
                workspace_slug=workspace_slug,
                name=name,
                description=description,
                functional_type=functional_type,
            )

        def create_pipeline_version(pipeline_code: str, source_code: str) -> dict:
            """Upload the Python source code as the first version (v1) of the pipeline.

            Only call this if create_pipeline returned success=true. Pass the pipeline code
            returned by create_pipeline and the full Python source as a single string.
            """
            return mcp_create_pipeline_version(
                user=user,
                workspace_slug=workspace_slug,
                pipeline_code=pipeline_code,
                source_code=source_code,
            )

        return [create_pipeline, create_pipeline_version]
