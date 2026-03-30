from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.mcp.tools import create_pipeline


class PipelineAgent(BaseAgent):
    instruction_set = InstructionSet.PIPELINE
    tool_names = [create_pipeline]
