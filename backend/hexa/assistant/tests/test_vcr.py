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

import json
import os
from unittest.mock import patch

import vcr
from asgiref.sync import async_to_sync
from django.test import TestCase, tag
from vcr.record_mode import RecordMode

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message
from hexa.user_management.models import AiSettings, Organization, User
from hexa.workspaces.models import Workspace


def run_agent(agent: BaseAgent, message: str) -> None:
    async def _consume():
        async for _ in agent.run_stream(message):
            pass

    async_to_sync(_consume)()


CASSETTES_DIR = os.path.join(os.path.dirname(__file__), "cassettes")


def _match_stream_mode(r1, r2):
    """Match requests by whether they use streaming, so concurrent naming and
    main-agent calls are routed to the correct cassette interactions regardless
    of which HTTP request arrives first.
    """
    try:
        b1 = json.loads(r1.body)
        b2 = json.loads(r2.body)
        return b1.get("stream") == b2.get("stream")
    except (json.JSONDecodeError, AttributeError):
        return True


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
    match_on=["method", "host", "port", "path", "stream_mode"],
)
assistant_vcr.register_matcher("stream_mode", _match_stream_mode)


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
        cls.organization = Organization.objects.create(name="VCR Test Org")
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="VCR Test WS", description="For VCR tests"
            )
        cls.workspace.organization = cls.organization
        cls.workspace.save()
        AiSettings.objects.update_or_create(
            organization=cls.organization,
            defaults={
                "enabled": True,
                "provider": AiSettings.Provider.ANTHROPIC,
                "model": AiSettings.Model.HAIKU,
                "api_key": os.environ.get(
                    "ANTHROPIC_API_KEY", "test-key-for-vcr-replay"
                ),
            },
        )

    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    @assistant_vcr.use_cassette(os.path.join(CASSETTES_DIR, "simple_chat.yaml"))
    def test_simple_chat_saves_messages_to_db(self):
        agent = BaseAgent(self.conversation)
        run_agent(agent, "Hello")
        self.assertEqual(
            self.conversation.messages.filter(role=Message.Role.USER).count(), 1
        )
        assistant_msg = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        ).first()
        self.assertIsNotNone(assistant_msg)
        self.assertIsInstance(assistant_msg.content, list)
        self.assertGreater(len(assistant_msg.content), 0)

    @assistant_vcr.use_cassette(os.path.join(CASSETTES_DIR, "simple_chat.yaml"))
    def test_simple_chat_generates_conversation_name(self):
        agent = BaseAgent(self.conversation)
        run_agent(agent, "Hello")
        self.conversation.refresh_from_db()
        self.assertIsNotNone(self.conversation.name)
        self.assertGreater(len(self.conversation.name), 0)
