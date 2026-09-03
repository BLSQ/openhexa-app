from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from hexa.assistant.agents.base import AgentModels, BaseAgent
from hexa.assistant.agents.create_pipeline_agent import CreatePipelineAgent
from hexa.assistant.agents.edit_pipeline_agent import EditPipelineAgent
from hexa.assistant.agents.edit_webapp_agent import EditWebappAgent
from hexa.assistant.agents.generate_sql_agent import GenerateSqlAgent
from hexa.assistant.instructions import InstructionSet

if TYPE_CHECKING:
    from hexa.assistant.models import Conversation

_AGENT_REGISTRY: dict[InstructionSet, type[BaseAgent]] = {
    InstructionSet.CREATE_PIPELINE: CreatePipelineAgent,
    InstructionSet.EDIT_PIPELINE: EditPipelineAgent,
    InstructionSet.EDIT_WEBAPP: EditWebappAgent,
    InstructionSet.GENERATE_SQL: GenerateSqlAgent,
    InstructionSet.GENERAL: BaseAgent,
}


def create_agent(
    conversation: Conversation, models: AgentModels | None = None
) -> BaseAgent:
    agent_class = _AGENT_REGISTRY.get(
        InstructionSet(conversation.instruction_set), BaseAgent
    )
    return agent_class(conversation, models)


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
        func.__name__
        for cls in _AGENT_REGISTRY.values()
        for func in cls.common_tools + cls.tools
    )
