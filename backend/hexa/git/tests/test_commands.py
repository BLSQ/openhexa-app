from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command

from hexa.core.test import TestCase
from hexa.git.forgejo import ForgejoAPIError
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, Webapp
from hexa.workspaces.models import Workspace


class ProtectGitBranchesCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.workspace = Workspace.objects.create(name="Cmd Workspace")
        cls.user = User.objects.create_user("cmd@bluesquarehub.com", "password")
        for slug in ("a", "b"):
            GitWebapp.objects.create(
                name=f"App {slug}",
                slug=slug,
                subdomain=f"cmd-{slug}",
                workspace=cls.workspace,
                created_by=cls.user,
                type=Webapp.WebappType.STATIC,
                repository=f"cmd-ws-webapp-{slug}",
            )

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_protects_every_repo(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        out = StringIO()

        call_command("protect_git_branches", stdout=out)

        self.assertEqual(client.protect_branch.call_count, 2)
        client.protect_branch.assert_any_call("no-org", "cmd-ws-webapp-a")
        client.protect_branch.assert_any_call("no-org", "cmd-ws-webapp-b")
        self.assertIn("protected=2 already_protected=0 failed=0", out.getvalue())

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_counts_already_protected_separately(self, mock_get_client):
        client = MagicMock()
        client.protect_branch.side_effect = [
            ForgejoAPIError("POST", "url", 409, "rule exists"),
            None,
        ]
        mock_get_client.return_value = client
        out = StringIO()

        call_command("protect_git_branches", stdout=out)

        self.assertIn("protected=1 already_protected=1 failed=0", out.getvalue())

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_reports_failures_and_continues(self, mock_get_client):
        client = MagicMock()
        client.protect_branch.side_effect = [
            ForgejoAPIError("POST", "url", 500, "boom"),
            None,
        ]
        mock_get_client.return_value = client
        out, err = StringIO(), StringIO()

        call_command("protect_git_branches", stdout=out, stderr=err)

        self.assertEqual(client.protect_branch.call_count, 2)
        self.assertIn("protected=1 already_protected=0 failed=1", out.getvalue())
