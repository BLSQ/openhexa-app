"""
VCR smoke tests for the assistant agent against real Anthropic API responses.

These tests replay pre-recorded HTTP cassettes (no live network needed).
To re-record cassettes:
  1. Set ANTHROPIC_API_KEY in your environment.
  2. Change record_mode to RecordMode.NEW_EPISODES in the decorator below.
  3. Run: docker compose run app test hexa.assistant.tests.test_vcr --settings=config.settings.test
  4. Commit the updated cassette files.
  5. Restore record_mode to 'none'.
"""

import os
from unittest.mock import patch

import vcr
from vcr.record_mode import RecordMode
from django.test import TestCase, tag

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message
from hexa.user_management.models import AiSettings, User
from hexa.workspaces.models import Workspace

CASSETTES_DIR = os.path.join(os.path.dirname(__file__), "cassettes")

assistant_vcr = vcr.VCR(
    filter_headers=[
        "x-api-key",
        "authorization",
        "x-stainless-os",
        "x-stainless-lang",
        "x-stainless-runtime",
        "x-stainless-runtime-version",
        "x-stainless-package-version",
        "user-agent",
    ],
    record_mode=RecordMode.NONE,
    match_on=["method", "host", "port", "path"],
)


@tag("vcr")
class AssistantVCRTest(TestCase):
    """
    Smoke tests that run the full agent stack (including AnthropicModel) against
    cassette-recorded HTTP responses. Run with --exclude-tag=vcr to skip in CI
    unless cassettes have been committed.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "vcr-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="VCR Test WS", description="For VCR tests"
            )
        AiSettings.objects.update_or_create(
            user=cls.user,
            defaults={
                "enabled": True,
                "provider": AiSettings.Provider.ANTHROPIC,
                "model": AiSettings.Model.HAIKU,
                "api_key": "test-key-for-vcr-replay",
            },
        )

    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    @assistant_vcr.use_cassette(os.path.join(CASSETTES_DIR, "simple_chat.yaml"))
    def test_simple_chat_returns_text_response(self):
        agent = BaseAgent(self.conversation)
        response = agent.run("Hello")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    @assistant_vcr.use_cassette(os.path.join(CASSETTES_DIR, "simple_chat.yaml"))
    def test_simple_chat_saves_messages_to_db(self):
        agent = BaseAgent(self.conversation)
        agent.run("Hello")
        self.assertEqual(
            self.conversation.messages.filter(role=Message.Role.USER).count(), 1
        )
        self.assertEqual(
            self.conversation.messages.filter(role=Message.Role.ASSISTANT).count(), 1
        )

    @assistant_vcr.use_cassette(os.path.join(CASSETTES_DIR, "simple_chat.yaml"))
    def test_simple_chat_generates_conversation_name(self):
        agent = BaseAgent(self.conversation)
        agent.run("Hello")
        self.conversation.refresh_from_db()
        self.assertIsNotNone(self.conversation.name)
        self.assertGreater(len(self.conversation.name), 0)
