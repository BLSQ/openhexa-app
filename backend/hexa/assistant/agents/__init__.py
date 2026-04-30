from __future__ import annotations

from typing import TYPE_CHECKING

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.create_pipeline_agent import CreatePipelineAgent
from hexa.assistant.agents.edit_pipeline_agent import EditPipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.model_builder import AiModelBuilder

if TYPE_CHECKING:
    from hexa.assistant.models import Conversation

_AGENT_REGISTRY: dict[InstructionSet, type[BaseAgent]] = {
    InstructionSet.CREATE_PIPELINE: CreatePipelineAgent,
    InstructionSet.EDIT_PIPELINE: EditPipelineAgent,
    InstructionSet.GENERAL: BaseAgent,
}


def create_agent(
    conversation: Conversation, builder: AiModelBuilder | None = None
) -> BaseAgent:
    agent_class = _AGENT_REGISTRY.get(
        InstructionSet(conversation.instruction_set), BaseAgent
    )
    if builder is not None:
        return agent_class(conversation, builder)
    return agent_class.from_conversation(conversation)
