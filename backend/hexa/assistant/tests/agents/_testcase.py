from unittest.mock import patch

from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class AgentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "agent-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="Test Workspace", description=""
            )
