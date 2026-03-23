from hexa.assistant.agent.agent import AssistantAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation


class PipelineAgent(AssistantAgent):
    instruction_set = InstructionSet.PIPELINE

    def _get_tools(self, conversation: Conversation) -> list:
        # Lazy import to avoid circular dependency
        from hexa.mcp.tools import create_pipeline as mcp_create_pipeline
        from hexa.mcp.tools import write_file as mcp_write_file

        user = conversation.user
        workspace_slug = conversation.workspace.slug

        def create_pipeline(
            name: str, description: str = "", functional_type: str = ""
        ) -> dict:
            """Create a new pipeline in the current workspace. Returns the pipeline id, code, and name."""
            return mcp_create_pipeline(
                user=user,
                workspace_slug=workspace_slug,
                name=name,
                description=description,
                functional_type=functional_type,
            )

        def write_pipeline_file(file_path: str, content: str) -> dict:
            """Write Python source code to a new file in the workspace bucket. Use this to create the starter pipeline file after calling create_pipeline."""
            return mcp_write_file(
                user=user,
                workspace_slug=workspace_slug,
                file_path=file_path,
                content=content,
            )

        return [create_pipeline, write_pipeline_file]
