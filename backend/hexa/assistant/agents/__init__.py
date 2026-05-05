from __future__ import annotations

from typing import TYPE_CHECKING

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.create_pipeline_agent import CreatePipelineAgent
from hexa.assistant.agents.edit_pipeline_agent import EditPipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.model_builder import BuiltModel

if TYPE_CHECKING:
    from hexa.assistant.models import Conversation

_AGENT_REGISTRY: dict[InstructionSet, type[BaseAgent]] = {
    InstructionSet.CREATE_PIPELINE: CreatePipelineAgent,
    InstructionSet.EDIT_PIPELINE: EditPipelineAgent,
    InstructionSet.GENERAL: BaseAgent,
}


def create_agent(
    conversation: Conversation, built_model: BuiltModel | None = None
) -> BaseAgent:
    agent_class = _AGENT_REGISTRY.get(
        InstructionSet(conversation.instruction_set), BaseAgent
    )
    return agent_class(conversation, built_model)
