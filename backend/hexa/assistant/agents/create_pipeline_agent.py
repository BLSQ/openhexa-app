from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.mcp.tools.help import get_help_or_doc
from hexa.mcp.tools.pipelines import create_pipeline


class CreatePipelineAgent(BaseAgent):
    # TODO: Add reading pipeline / pipeline templates tools
    instruction_set = InstructionSet.CREATE_PIPELINE
    tools = [get_help_or_doc, create_pipeline]
    max_tokens = 8192
