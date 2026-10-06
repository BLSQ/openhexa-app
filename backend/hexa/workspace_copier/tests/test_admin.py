from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from hexa.user_management.models import User
from hexa.workspace_copier.models import (
    WorkspaceCopyJob,
    WorkspaceCopyRun,
    WorkspaceCopyRunStatus,
)

FORM_DATA = {
    "source_url": "https://api.source.example.org/graphql/",
    "source_token": "src-secret",
    "source_slug": "my-ws",
    "target_url": "https://api.target.example.org/graphql/",
    "target_token": "tgt-secret",
    "target_mode": "new",
    "target_organization": "org-1",
    "resources": ["workspace", "files"],
}


class CopyWorkspaceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_user(
            "root@openhexa.org", "password", is_superuser=True, is_staff=True
        )
        cls.staff = User.objects.create_user(
            "staff@openhexa.org", "password", is_staff=True
        )

    def setUp(self):
        self.url = reverse("admin:workspaces_workspace_copy")

    @patch("hexa.workspace_copier.queue.run_copy")
    def test_post_queues_a_run_without_running_the_copy(self, mock_run_copy):
        self.client.force_login(self.superuser)

        response = self.client.post(self.url, FORM_DATA)

        run = WorkspaceCopyRun.objects.get()
        self.assertRedirects(
            response,
            reverse("admin:workspace_copier_workspacecopyrun_change", args=[run.id]),
            fetch_redirect_response=False,
        )
        self.assertEqual(run.status, WorkspaceCopyRunStatus.QUEUED)
        self.assertEqual(run.created_by, self.superuser)
        self.assertEqual(run.resources, ["files", "workspace"])
        self.assertEqual(run.source_token, "src-secret")
        mock_run_copy.assert_not_called()

        job = WorkspaceCopyJob.objects.get()
        self.assertEqual(job.task, "run_workspace_copy")
        self.assertEqual(job.args, {"run_id": str(run.id)})

    def test_invalid_form_queues_nothing(self):
        self.client.force_login(self.superuser)

        response = self.client.post(self.url, {**FORM_DATA, "target_organization": ""})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(WorkspaceCopyRun.objects.exists())
        self.assertFalse(WorkspaceCopyJob.objects.exists())

    def test_non_superuser_is_forbidden(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.url).status_code, 403)


class WorkspaceCopyRunAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_user(
            "root@openhexa.org", "password", is_superuser=True, is_staff=True
        )

    def _change_url(self, run):
        return reverse("admin:workspace_copier_workspacecopyrun_change", args=[run.id])

    def test_run_page_never_shows_tokens(self):
        run = WorkspaceCopyRun.objects.create(
            source_slug="my-ws", source_token="src-secret", target_token="tgt-secret"
        )
        self.client.force_login(self.superuser)

        response = self.client.get(self._change_url(run))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "src-secret")
        self.assertNotContains(response, "tgt-secret")

    def test_active_run_page_refreshes_itself(self):
        run = WorkspaceCopyRun.objects.create(
            source_slug="my-ws", status=WorkspaceCopyRunStatus.RUNNING
        )
        self.client.force_login(self.superuser)

        response = self.client.get(self._change_url(run))

        self.assertContains(response, 'http-equiv="refresh"')
