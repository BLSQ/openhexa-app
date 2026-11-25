from unittest.mock import patch

from hexa.assistant.models import AssistantUser, Conversation
from hexa.core.test import TestCase
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace
from hexa.workspaces.tests.testutils import create_workspace


class AssistantUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "assistant-user@openhexa.org", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.WORKSPACE = create_workspace(cls.USER, name="Here", description="")
            cls.OTHER = create_workspace(cls.USER, name="Elsewhere", description="")
        cls.OTHER_PIPELINE = Pipeline.objects.create(
            workspace=cls.OTHER, name="Elsewhere", code="elsewhere"
        )

    def setUp(self):
        self.assistant_user = AssistantUser.from_conversation(
            Conversation.objects.create(user=self.USER, workspace=self.WORKSPACE)
        )

    def test_reaches_only_the_conversation_workspace(self):
        self.assertEqual(
            [self.WORKSPACE],
            list(Workspace.objects.filter_for_user(self.assistant_user)),
        )
        self.assertFalse(
            Pipeline.objects.filter_for_user(self.assistant_user)
            .filter(pk=self.OTHER_PIPELINE.pk)
            .exists()
        )

    def test_reaches_nothing_once_ai_is_blocked_on_the_workspace(self):
        Workspace.objects.filter(pk=self.WORKSPACE.pk).update(ai_enabled=False)

        self.assertFalse(
            Workspace.objects.filter_for_user(self.assistant_user).exists()
        )

    def test_acts_for_the_conversation_person(self):
        self.assertEqual(self.USER, self.assistant_user.real_user)
        self.assertEqual(self.USER.pk, self.assistant_user.pk)
