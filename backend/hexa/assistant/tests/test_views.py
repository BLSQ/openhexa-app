import asyncio
import json
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from django.urls import reverse

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


def _parse_sse(content: bytes) -> list[dict]:
    events = []
    current: dict = {}
    for line in content.decode().splitlines():
        if line.startswith("event:"):
            current["event"] = line[len("event:") :].strip()
        elif line.startswith("data:"):
            current["data"] = json.loads(line[len("data:") :].strip())
        elif not line and current:
            events.append(current)
            current = {}
    return events


async def _collect_async_stream(streaming_content) -> bytes:
    chunks = []
    async for chunk in streaming_content:
        chunks.append(chunk)
    return b"".join(chunks)


def _url(conversation_id):
    return reverse("assistant:stream_assistant_message", args=[conversation_id])


def _post(client, conversation_id, body=None, content_type="application/json"):
    payload = json.dumps(body or {"message": "Hello"})
    return client.post(_url(conversation_id), payload, content_type=content_type)


class StreamAssistantMessageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "view-test@example.com", "password", is_superuser=True
        )
        cls.other_user = User.objects.create_user(
            "view-other@example.com", "password"
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="View Test WS", description=""
            )

    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    # --- Method ---

    def test_get_returns_405(self):
        self.client.force_login(self.user)
        response = self.client.get(_url(self.conversation.id))
        self.assertEqual(response.status_code, 405)

    # --- Auth ---

    def test_unauthenticated_returns_401(self):
        response = _post(self.client, self.conversation.id)
        self.assertEqual(response.status_code, 401)

    # --- Input validation ---

    def test_invalid_json_body_returns_400(self):
        self.client.force_login(self.user)
        response = self.client.post(
            _url(self.conversation.id), "not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_message_returns_400(self):
        self.client.force_login(self.user)
        response = _post(self.client, self.conversation.id, {"message": "  "})
        self.assertEqual(response.status_code, 400)

    # --- Authorization ---

    def test_conversation_of_other_user_returns_404(self):
        self.client.force_login(self.other_user)
        response = _post(self.client, self.conversation.id)
        self.assertEqual(response.status_code, 404)

    def test_unknown_conversation_id_returns_404(self):
        self.client.force_login(self.user)
        response = _post(self.client, uuid.uuid4())
        self.assertEqual(response.status_code, 404)

    # --- Monthly limit ---

    def test_monthly_limit_exceeded_returns_429(self):
        self.client.force_login(self.user)
        with patch(
            "hexa.assistant.views.Conversation.get_monthly_cost_for_user",
            return_value=Decimal("999"),
        ):
            response = _post(self.client, self.conversation.id)
        self.assertEqual(response.status_code, 429)

    # --- Happy path ---

    def test_valid_request_returns_sse_stream(self):
        self.client.force_login(self.user)

        async def _fake_stream(self, _message):
            yield b'event: text_delta\ndata: {"delta": "Hello"}\n\n'
            yield b'event: done\ndata: {"message_id": "abc"}\n\n'

        class _FakeAgent:
            run_stream = _fake_stream

        with patch("hexa.assistant.agents.create_agent", return_value=_FakeAgent()):
            response = _post(self.client, self.conversation.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/event-stream")
        self.assertEqual(response["Cache-Control"], "no-cache")

        events = _parse_sse(
            asyncio.run(_collect_async_stream(response.streaming_content))
        )
        self.assertEqual(events[0]["event"], "text_delta")
        self.assertEqual(events[0]["data"]["delta"], "Hello")
        self.assertEqual(events[1]["event"], "done")
