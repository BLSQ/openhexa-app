import logfire
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message

from ._helpers import (
    FakeModelBuilder,
    _AgentWithFakeTool,
    _make_tool_call_model,
    run_agent,
)
from ._testcase import AgentTestCase


class InstrumentedAgentTest(AgentTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logfire.configure(send_to_logfire=False, console=False)
        logfire.instrument_pydantic_ai()

    @classmethod
    def tearDownClass(cls):
        Agent.instrument_all(False)
        super().tearDownClass()

    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def test_instrumented_run_completes(self):
        agent = BaseAgent(
            self.conversation,
            FakeModelBuilder(TestModel(call_tools=[], custom_output_text="Hi!")),
        )
        run_agent(agent, "Hello")
        assistant_msg = self.conversation.messages.get(role=Message.Role.ASSISTANT)
        self.assertEqual(assistant_msg.content[0]["content"], "Hi!")
        self.assertGreater(assistant_msg.input_tokens, 0)

    def test_instrumented_tool_call_completes(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        agent = _AgentWithFakeTool(self.conversation, FakeModelBuilder(model))
        run_agent(agent, "Use the tool")
        self.assertTrue(self.first_tool_invocation(self.conversation).success)
