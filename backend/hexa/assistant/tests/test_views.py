import asyncio
import json
import uuid
from unittest.mock import patch

from django.core.exceptions import PermissionDenied
from django.urls import reverse

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.core.test import TestCase
from hexa.core.test.utils import collect_async_stream, parse_sse_stream
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import Organization, User
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace


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
        cls.other_user = User.objects.create_user("view-other@example.com", "password")
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = create_workspace(
                cls.user,
                name="View Test WS",
                description="",
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

    # --- Workspace AI block ---

    def test_workspace_with_ai_disabled_returns_403(self):
        self.workspace.ai_enabled = False
        self.workspace.save()
        self.client.force_login(self.user)
        response = _post(self.client, self.conversation.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error_code"], "AI_DISABLED_FOR_WORKSPACE")

    def test_a_conversation_linked_to_another_workspace_returns_403(self):
        with patch("hexa.workspaces.models.create_database"):
            other = create_workspace(self.user, name="Other WS", description="")
        self.conversation.linked_object = Pipeline.objects.create(
            workspace=other, name="Other", code="other"
        )
        self.conversation.save()
        self.client.force_login(self.user)

        response = _post(self.client, self.conversation.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["error_code"], "LINKED_OBJECT_OUTSIDE_WORKSPACE"
        )

    def test_a_conversation_cannot_be_started_in_a_workspace_with_ai_disabled(self):
        editor = User.objects.create_user("view-editor@example.com", "password")
        WorkspaceMembership.objects.create(
            workspace=self.workspace, user=editor, role=WorkspaceMembershipRole.EDITOR
        )
        self.assertTrue(
            editor.has_perm("assistant.create_conversation", self.workspace)
        )

        self.workspace.ai_enabled = False
        self.workspace.save()

        with self.assertRaises(PermissionDenied):
            Conversation.objects.create_if_has_perm(editor, self.workspace)

    # --- Organization AI budget ---

    def test_organization_ai_budget_exceeded_returns_403(self):
        org = Organization.objects.create(name="Budget Org", short_name="BORG")
        self.workspace.organization = org
        self.workspace.save()
        self.client.force_login(self.user)
        with patch(
            "hexa.user_management.models.Organization.is_ai_budget_limit_reached",
            return_value=True,
        ):
            response = _post(self.client, self.conversation.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error_code"], "AI_BUDGET_EXCEEDED")

    # --- Happy path ---

    def test_valid_request_returns_sse_stream(self):
        org = Organization.objects.create(name="Budget Org", short_name="BORG")
        self.workspace.organization = org
        self.workspace.save()
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

        events = parse_sse_stream(
            asyncio.run(collect_async_stream(response.streaming_content))
        )
        self.assertEqual(events[0]["event"], "text_delta")
        self.assertEqual(events[0]["data"]["delta"], "Hello")
        self.assertEqual(events[1]["event"], "done")
