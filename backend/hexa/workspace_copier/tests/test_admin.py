from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from hexa.user_management.models import Organization, User
from hexa.workspace_copier.models import (
    WorkspaceCopyJob,
    WorkspaceCopyRun,
    WorkspaceCopyRunStatus,
)
from hexa.workspaces.models import Workspace

FORM_DATA = {
    "source_server": "custom",
    "source_url": "https://api.source.example.org/graphql/",
    "source_token": "src-secret",
    "source_slug": "my-ws",
    "target_server": "custom",
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
        # An unticked checkbox is absent from the POST.
        self.assertFalse(run.include_connection_secrets)
        self.assertFalse(run.same_server)
        self.assertTrue(run.verify_ssl)
        self.assertEqual(run.source_url, FORM_DATA["source_url"])
        mock_run_copy.assert_not_called()

        job = WorkspaceCopyJob.objects.get()
        self.assertEqual(job.task, "run_workspace_copy")
        self.assertEqual(job.args, {"run_id": str(run.id)})

    def test_disabling_ssl_verification_is_stored_on_the_run(self):
        self.client.force_login(self.superuser)

        self.client.post(self.url, {**FORM_DATA, "disable_ssl_verification": "on"})

        self.assertFalse(WorkspaceCopyRun.objects.get().verify_ssl)

    def test_this_server_is_stored_as_a_blank_url(self):
        self.client.force_login(self.superuser)

        self.client.post(self.url, {**FORM_DATA, "source_server": ""})

        run = WorkspaceCopyRun.objects.get()
        self.assertEqual(run.source_url, "")
        self.assertFalse(run.same_server)

    def test_this_server_on_both_sides_queues_a_same_server_copy(self):
        self.client.force_login(self.superuser)

        self.client.post(
            self.url, {**FORM_DATA, "source_server": "", "target_server": ""}
        )

        self.assertTrue(WorkspaceCopyRun.objects.get().same_server)

    def test_invalid_form_queues_nothing(self):
        self.client.force_login(self.superuser)

        response = self.client.post(self.url, {**FORM_DATA, "target_organization": ""})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(WorkspaceCopyRun.objects.exists())
        self.assertFalse(WorkspaceCopyJob.objects.exists())

    def test_non_superuser_is_forbidden(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.url).status_code, 403)


class CopyLookupViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_user(
            "root@openhexa.org", "password", is_superuser=True, is_staff=True
        )
        cls.staff = User.objects.create_user(
            "staff@openhexa.org", "password", is_staff=True
        )
        cls.organization = Organization.objects.create(
            name="Ministry of Health", short_name="moh"
        )
        Organization.objects.create(name="Other organization")
        Workspace.objects.create(
            name="Malaria analysis",
            slug="malaria",
            db_name="malaria",
            organization=cls.organization,
        )
        Workspace.objects.create(
            name="Old malaria data",
            slug="malaria-old",
            db_name="malariaold",
            organization=cls.organization,
            archived=True,
        )
        Workspace.objects.create(
            name="Nutrition",
            slug="nutrition",
            db_name="nutrition",
            organization=cls.organization,
        )

    def setUp(self):
        self.url = reverse("admin:workspaces_workspace_copy_lookup")

    def _results(self, **params):
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        return response.json()["results"]

    def test_non_superuser_is_forbidden(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_workspaces_match_on_slug_or_name(self):
        # The superuser is a member of none of them: the search is instance-wide.
        self.client.force_login(self.superuser)

        self.assertEqual(
            self._results(kind="workspace", q="MALAR"),
            [{"id": "malaria", "text": "malaria — Malaria analysis"}],
        )
        self.assertEqual(
            self._results(kind="workspace", q="nutri"),
            [{"id": "nutrition", "text": "nutrition — Nutrition"}],
        )

    def test_organizations_return_their_id(self):
        self.client.force_login(self.superuser)

        self.assertEqual(
            self._results(kind="organization", q="moh"),
            [{"id": str(self.organization.id), "text": "Ministry of Health"}],
        )

    def test_results_are_capped(self):
        Workspace.objects.bulk_create(
            Workspace(
                name=f"Bulk {i}",
                slug=f"bulk-{i:02}",
                db_name=f"bulk{i:02}",
                organization=self.organization,
            )
            for i in range(25)
        )
        self.client.force_login(self.superuser)

        self.assertEqual(len(self._results(kind="workspace", q="bulk")), 20)


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

    def test_list_and_run_page_with_deferred_logs(self):
        run = WorkspaceCopyRun.objects.create(
            source_slug="my-ws", logs="copied file a.csv\n", summary="1 file"
        )
        self.client.force_login(self.superuser)

        list_response = self.client.get(
            reverse("admin:workspace_copier_workspacecopyrun_changelist")
        )
        run_response = self.client.get(self._change_url(run))

        self.assertContains(list_response, "my-ws")
        self.assertNotContains(list_response, "copied file a.csv")
        self.assertContains(run_response, "copied file a.csv")
        self.assertContains(run_response, "1 file")

    def test_list_links_to_the_copy_form(self):
        self.client.force_login(self.superuser)

        response = self.client.get(
            reverse("admin:workspace_copier_workspacecopyrun_changelist")
        )

        self.assertContains(response, reverse("admin:workspaces_workspace_copy"))

    def test_active_run_page_refreshes_itself(self):
        run = WorkspaceCopyRun.objects.create(
            source_slug="my-ws", status=WorkspaceCopyRunStatus.RUNNING
        )
        self.client.force_login(self.superuser)

        response = self.client.get(self._change_url(run))

        self.assertContains(response, 'http-equiv="refresh"')
