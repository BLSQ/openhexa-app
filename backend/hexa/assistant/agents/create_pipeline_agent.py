import logging

from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.mcp.tools.help import get_help_or_doc
from hexa.mcp.tools.pipelines import create_pipeline
from hexa.pipelines.models import Pipeline

logger = logging.getLogger(__name__)


class CreatePipelineAgent(BaseAgent):
    instruction_set = InstructionSet.CREATE_PIPELINE
    tools = [get_help_or_doc, create_pipeline]
    max_tokens = 32768

    async def _on_tool_result(self, invocation) -> None:
        if invocation.tool_name != "create_pipeline" or not invocation.success:
            return
        pipeline_id = (invocation.tool_output or {}).get("pipeline", {}).get("id")
        if not pipeline_id:
            return
        try:
            pipeline = await Pipeline.objects.aget(id=pipeline_id)
            ct = await sync_to_async(ContentType.objects.get_for_model)(Pipeline)
            self.conversation.linked_object_content_type = ct
            self.conversation.linked_object_id = pipeline.id
            self.conversation.instruction_set = InstructionSet.EDIT_PIPELINE
            await self.conversation.asave(
                update_fields=[
                    "linked_object_content_type",
                    "linked_object_id",
                    "instruction_set",
                ]
            )
        except Exception:
            logger.exception(
                "CreatePipelineAgent: failed to link conversation %s to pipeline %s",
                self.conversation.id,
                pipeline_id,
            )
