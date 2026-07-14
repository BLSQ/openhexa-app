from unittest.mock import patch

from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.core.test import TestCase
from hexa.user_management.models import Organization, User
from hexa.workspaces.models import Workspace


class AgentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "agent-test@example.com", "password", is_superuser=True
        )
        cls.ORGANIZATION = Organization.objects.create(name="Agent Test Org")
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user,
                name="Test Workspace",
                description="",
                organization=cls.ORGANIZATION,
            )

    @staticmethod
    def first_tool_invocation(conversation: Conversation) -> ToolInvocation:
        return (
            conversation.messages.filter(role=Message.Role.ASSISTANT)
            .first()
            .tool_invocations.first()
        )
