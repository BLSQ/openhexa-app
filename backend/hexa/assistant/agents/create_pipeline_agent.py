import logging

from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.mcp.tools.help import get_help_or_doc
from hexa.mcp.tools.pipelines import create_pipeline

logger = logging.getLogger(__name__)


class CreatePipelineAgent(BaseAgent):
    instruction_set = InstructionSet.CREATE_PIPELINE
    tools = [get_help_or_doc, create_pipeline]
    max_tokens = 32768
    

    async def _persist_run(
        self,
        response_text,
        tool_invocations,
        usage,
        all_messages,
        is_first_message,
        precomputed_naming=None,
    ):
        result = await super()._persist_run(
            response_text,
            tool_invocations,
            usage,
            all_messages,
            is_first_message,
            precomputed_naming=precomputed_naming,
        )
        await self._link_created_pipeline(tool_invocations)
        return result

    async def _link_created_pipeline(self, tool_invocations):
        for inv in tool_invocations.values():
            if inv.tool_name != "create_pipeline" or not inv.success:
                continue
            pipeline_id = (inv.tool_output or {}).get("pipeline", {}).get("id")
            if not pipeline_id:
                continue
            try:
                from hexa.pipelines.models import Pipeline

                pipeline = await Pipeline.objects.aget(id=pipeline_id)
                ct = await sync_to_async(ContentType.objects.get_for_model)(Pipeline)
                self.conversation.linked_object_content_type = ct
                self.conversation.linked_object_id = pipeline.id
                await self.conversation.asave(
                    update_fields=["linked_object_content_type", "linked_object_id"]
                )
            except Exception:
                logger.exception(
                    "CreatePipelineAgent: failed to link conversation %s to pipeline %s",
                    self.conversation.id,
                    pipeline_id,
                )
            break
