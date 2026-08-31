from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import (
    WORKSPACE_DESCRIPTION_MAX_CHARS,
    BaseAgent,
)
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.workspaces.models import DEFAULT_WORKSPACE_DESCRIPTION

from ._helpers import make_built_model
from ._testcase import AgentTestCase


class _AgentWithExtraInstructions(BaseAgent):
    def _extra_instructions(self) -> str:
        return "EXTRA MARKER"


class WorkspaceInstructionsTest(AgentTestCase):
    def setUp(self):
        super().setUp()
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def _make_agent(self, agent_class=BaseAgent) -> BaseAgent:
        return agent_class(self.conversation, built_model=make_built_model(TestModel()))

    def _set_description(self, description: str) -> None:
        self.workspace.description = description
        self.workspace.save()

    def test_blank_description_injects_nothing(self):
        for description in ("", "   \n"):
            with self.subTest(description=repr(description)):
                self._set_description(description)
                agent = self._make_agent()
                self.assertEqual(agent._workspace_instructions(), "")
                self.assertNotIn("Workspace notes", agent._build_instructions())

    def test_default_boilerplate_is_skipped(self):
        self._set_description(
            DEFAULT_WORKSPACE_DESCRIPTION.format(
                workspace_name=self.workspace.name,
                workspace_slug=self.workspace.slug,
            )
        )
        agent = self._make_agent()
        self.assertEqual(agent._workspace_instructions(), "")

    def test_default_boilerplate_skipped_after_rename(self):
        self._set_description(
            DEFAULT_WORKSPACE_DESCRIPTION.format(
                workspace_name=self.workspace.name,
                workspace_slug=self.workspace.slug,
            )
        )
        self.workspace.name = "Renamed Workspace"
        self.workspace.save()
        agent = self._make_agent()
        self.assertEqual(agent._workspace_instructions(), "")

    def test_edited_boilerplate_is_injected(self):
        self._set_description(
            DEFAULT_WORKSPACE_DESCRIPTION.format(
                workspace_name=self.workspace.name,
                workspace_slug=self.workspace.slug,
            )
            + "\n\nAlways use ISO country codes."
        )
        agent = self._make_agent()
        self.assertIn("Always use ISO country codes.", agent._workspace_instructions())

    def test_custom_description_is_injected(self):
        self._set_description("Always use ISO country codes.")
        agent = self._make_agent()
        instructions = agent._build_instructions()
        self.assertIn("## Workspace notes", instructions)
        self.assertIn(
            "<workspace_description>\nAlways use ISO country codes.\n"
            "</workspace_description>",
            instructions,
        )
        self.assertNotIn("truncated", instructions)

    def test_long_description_is_truncated(self):
        head = "x" * WORKSPACE_DESCRIPTION_MAX_CHARS
        self._set_description(head + "TAIL MARKER")
        agent = self._make_agent()
        block = agent._workspace_instructions()
        self.assertIn(head, block)
        self.assertNotIn("TAIL MARKER", block)
        self.assertIn("truncated", block)
        self.assertIn("get_workspace", block)
        self.assertIn(self.workspace.slug, block)

    def test_subclass_extra_instructions_come_after_workspace_block(self):
        self._set_description("Always use ISO country codes.")
        agent = self._make_agent(_AgentWithExtraInstructions)
        instructions = agent._build_instructions()
        self.assertIn("EXTRA MARKER", instructions)
        self.assertLess(
            instructions.index("## Workspace notes"),
            instructions.index("EXTRA MARKER"),
        )
