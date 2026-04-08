from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.mcp.tools.pipelines import create_pipeline


class PipelineAgent(BaseAgent):
    # TODO: Add reading pipeline / pipeline templates tools
    instruction_set = InstructionSet.PIPELINE
    tools = [create_pipeline]
