from __future__ import annotations

from typing import TYPE_CHECKING

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.pipeline_agent import PipelineAgent
from hexa.assistant.instructions import InstructionSet

if TYPE_CHECKING:
    from hexa.assistant.models import Conversation

_AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    InstructionSet.PIPELINE: PipelineAgent,
    InstructionSet.GENERAL: BaseAgent,
}


def create_agent(conversation: Conversation) -> BaseAgent:
    agent_class = _AGENT_REGISTRY.get(
        InstructionSet(conversation.instruction_set), BaseAgent
    )
    return agent_class(conversation)
