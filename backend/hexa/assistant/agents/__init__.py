from hexa.assistant.agents.agent import AssistantAgent
from hexa.assistant.agents.pipeline_agent import PipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation

_AGENT_REGISTRY: dict[InstructionSet, type[AssistantAgent]] = {
    InstructionSet.PIPELINE: PipelineAgent,
    InstructionSet.GENERAL: AssistantAgent,
}


def create_agent(conversation: Conversation) -> AssistantAgent:
    agent_class = _AGENT_REGISTRY.get(
        InstructionSet(conversation.instruction_set), AssistantAgent
    )
    return agent_class(conversation)
