from pydantic_ai.models.test import TestModel

from hexa.assistant.agents import create_agent
from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.create_pipeline_agent import CreatePipelineAgent
from hexa.assistant.agents.edit_pipeline_agent import EditPipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation

from ._helpers import make_built_model
from ._testcase import AgentTestCase


class AgentRegistryTest(AgentTestCase):
    def test_pipeline_instruction_set_returns_pipeline_agent(self):
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.CREATE_PIPELINE,
        )
        self.assertIsInstance(
            create_agent(conversation, make_built_model(TestModel())),
            CreatePipelineAgent,
        )

    def test_general_instruction_set_returns_base_agent(self):
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )
        agent = create_agent(conversation, make_built_model(TestModel()))
        self.assertIsInstance(agent, BaseAgent)
        self.assertNotIsInstance(agent, CreatePipelineAgent)

    def test_unregistered_instruction_set_defaults_to_base_agent(self):
        # CREATE_WEBAPPS is a valid InstructionSet value but has no dedicated agent class.
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.CREATE_WEBAPPS,
        )
        self.assertIsInstance(
            create_agent(conversation, make_built_model(TestModel())), BaseAgent
        )

    def test_edit_pipeline_instruction_set_returns_edit_pipeline_agent(self):
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        self.assertIsInstance(
            create_agent(conversation, make_built_model(TestModel())), EditPipelineAgent
        )
