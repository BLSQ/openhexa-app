from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.create_pipeline_agent import CreatePipelineAgent
from hexa.assistant.agents.edit_pipeline_agent import EditPipelineAgent
from hexa.assistant.agents.edit_webapp_agent import EditWebappAgent
from hexa.assistant.agents.generate_sql_agent import GenerateSqlAgent
from hexa.assistant.agents.naming_agent import NamingAgent
from hexa.assistant.instructions import InstructionSet

if TYPE_CHECKING:
    from hexa.assistant.model_builder import AiModelBuilder
    from hexa.assistant.models import Conversation

_AGENT_REGISTRY: dict[InstructionSet, type[BaseAgent]] = {
    InstructionSet.CREATE_PIPELINE: CreatePipelineAgent,
    InstructionSet.EDIT_PIPELINE: EditPipelineAgent,
    InstructionSet.EDIT_WEBAPP: EditWebappAgent,
    InstructionSet.GENERATE_SQL: GenerateSqlAgent,
    InstructionSet.GENERAL: BaseAgent,
}


def pinnable_agent_keys() -> frozenset[str]:
    """Agents whose model can be pinned through ASSISTANT_AGENT_MODELS.

    An agent opts in by declaring an ``agent_key``; the ones that do not run on
    whatever model the organization configured, so a stray entry in the setting
    can never downgrade an organization's main assistant.
    """
    agents = (*_AGENT_REGISTRY.values(), NamingAgent)
    return frozenset(cls.agent_key for cls in agents if cls.agent_key)


def create_agent(
    conversation: Conversation, builder: AiModelBuilder | None = None
) -> BaseAgent:
    agent_class = _AGENT_REGISTRY.get(
        InstructionSet(conversation.instruction_set), BaseAgent
    )
    return agent_class(conversation, builder)


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
