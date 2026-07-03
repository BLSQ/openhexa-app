from __future__ import annotations

from functools import cache
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


@cache
def all_agent_tool_names() -> frozenset[str]:
    """Names of every tool any agent can call — i.e. every tool name that can
    surface in a conversation, and therefore in the frontend. This is the union
    across agents, so it includes agent-only tools like ``propose_pipeline_version``
    that are not in ``hexa.mcp.tools``. Must stay in sync with the
    ``AssistantToolName`` enum in the assistant GraphQL schema (a unit test
    enforces this).
    """
    return frozenset(
        func.__name__ for cls in _AGENT_REGISTRY.values() for func in cls.tools
    )
