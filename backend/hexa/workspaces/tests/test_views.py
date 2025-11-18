from urllib.parse import quote

from django.core.signing import Signer
from django.urls import reverse

from hexa.core.test import TestCase
from hexa.databases.api import get_db_server_credentials
from hexa.pipelines.models import Pipeline, PipelineRunTrigger
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
        )

        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword", is_superuser=True
        )

        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_JULIA,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE_MEMBERSHIP_JULIA = WorkspaceMembership.objects.get(
            workspace=cls.WORKSPACE, user=cls.USER_JULIA
        )

        cls.WORKSPACE_MEMBERSHIP_REBECCA = WorkspaceMembership.objects.create(
            user=cls.USER_REBECCA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test pipeline",
            code="my-pipeline",
            description="This is a test pipeline",
        )
        cls.PIPELINE.upload_new_version(
            cls.USER_JULIA, zipfile=b"", parameters=[], name="Version"
        )

    def test_workspace_credentials_401_no_permission(self):
        """User without any access to workspace gets 401"""
        self.client.force_login(self.USER_JANE)
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
        )
        self.assertEqual(response.status_code, 401)

    def test_workspace_credentials_anonymous(self):
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
        )
        self.assertEqual(response.status_code, 401)

    def test_credentials_no_workspace(self):
        response = self.client.post(
            reverse("workspaces:credentials"),
        )
        self.assertEqual(response.status_code, 400)

    def test_workspace_credentials_for_notebooks_401(self):
        self.client.force_login(self.USER_REBECCA)
        response = self.client.post(
            reverse(
                "workspaces:credentials",
            ),
            data={"workspace": self.WORKSPACE.slug},
        )
        self.assertEqual(response.status_code, 401)

    def test_workspace_for_notebooks_credentials_200(self):
        self.client.force_login(self.USER_JULIA)
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
        )

        db_credentials = get_db_server_credentials()

        self.maxDiff = None

        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.maxDiff = None

        # Expected URL should include application_name with user + workspace
        expected_db_url = (
            f"{self.WORKSPACE.db_url}"
            f"?application_name={quote(f'notebook /user/{self.USER_JULIA.email}/{self.WORKSPACE.slug}')}"
        )

        self.assertEqual(
            response_data["env"],
            {
                "WORKSPACE_BUCKET_NAME": self.WORKSPACE.bucket_name,
                "WORKSPACE_DATABASE_DB_NAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_HOST": self.WORKSPACE.db_host,
                "WORKSPACE_DATABASE_PORT": db_credentials["port"],
                "WORKSPACE_DATABASE_USERNAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_PASSWORD": self.WORKSPACE.db_password,
                "WORKSPACE_DATABASE_URL": expected_db_url,
                "WORKSPACE_STORAGE_ENGINE": "dummy",
                "HEXA_TOKEN": Signer().sign_object(
                    self.WORKSPACE_MEMBERSHIP_JULIA.access_token
                ),
            },
        )
        self.assertEqual(
            response_data["notebooks_server_hash"],
            self.WORKSPACE.workspacemembership_set.get(
                user=self.USER_JULIA
            ).notebooks_server_hash,
        )

    def test_pipeline_invalid_credentials_404(
        self,
    ):
        run = self.PIPELINE.run(
            self.USER_JULIA, self.PIPELINE.last_version, PipelineRunTrigger.MANUAL, {}
        )
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
            **{
                "HTTP_Authorization": f"Bearer {Signer().sign_object(run.access_token + 'invalid')}"
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_pipeline_credentials_200(self):
        run = self.PIPELINE.run(
            self.USER_JULIA, self.PIPELINE.last_version, PipelineRunTrigger.MANUAL, {}
        )

        token = Signer().sign_object(run.access_token)

        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": self.WORKSPACE.slug},
            **{"HTTP_Authorization": f"Bearer {token}"},
        )

        db_credentials = get_db_server_credentials()

        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.maxDiff = None

        # Expected URL should include application_name with pipeline name and run ID
        expected_db_url = (
            f"{self.WORKSPACE.db_url}"
            f"?application_name={quote(f'{self.WORKSPACE.slug} - {self.PIPELINE.name} (run {run.id})')}"
        )

        self.assertEqual(
            response_data["env"],
            {
                "WORKSPACE_BUCKET_NAME": self.WORKSPACE.bucket_name,
                "WORKSPACE_DATABASE_DB_NAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_HOST": self.WORKSPACE.db_host,
                "WORKSPACE_DATABASE_PORT": db_credentials["port"],
                "WORKSPACE_DATABASE_USERNAME": self.WORKSPACE.db_name,
                "WORKSPACE_DATABASE_PASSWORD": self.WORKSPACE.db_password,
                "WORKSPACE_DATABASE_URL": expected_db_url,
                "WORKSPACE_STORAGE_ENGINE": "dummy",
                "HEXA_TOKEN": token,
            },
        )
        self.assertEqual(
            response_data["notebooks_server_hash"],
            str(run.id),
        )

    def test_org_admin_auto_creates_membership(self):
        """Test that org admin without membership gets auto-created membership when launching notebooks"""
        org = Organization.objects.create(name="Test Org")
        org_admin = User.objects.create_user("admin@org.com", "password")
        OrganizationMembership.objects.create(
            organization=org,
            user=org_admin,
            role=OrganizationMembershipRole.ADMIN,
        )

        workspace = Workspace.objects.create_if_has_perm(
            self.USER_JULIA,
            name="Test Workspace",
            description="Test workspace for org admin",
            organization=org,
        )

        self.assertFalse(
            WorkspaceMembership.objects.filter(
                workspace=workspace, user=org_admin
            ).exists()
        )

        self.client.force_login(org_admin)
        response = self.client.post(
            reverse("workspaces:credentials"),
            data={"workspace": workspace.slug},
        )

        self.assertEqual(response.status_code, 200)

        membership = WorkspaceMembership.objects.get(
            workspace=workspace, user=org_admin
        )
        self.assertEqual(membership.role, WorkspaceMembershipRole.ADMIN)

        response_data = response.json()
        self.assertIn("env", response_data)
        self.assertIn("notebooks_server_hash", response_data)
        self.assertEqual(
            response_data["notebooks_server_hash"], membership.notebooks_server_hash
        )
