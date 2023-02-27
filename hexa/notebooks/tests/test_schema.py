import responses
from django.conf import settings

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class NotebooksTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )

        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
        )

        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com", "juliaspassword"
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_JULIA
        )

        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "workspaceroot@bluesquarehub.com",
            "workspace",
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_JULIA,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
            countries=[{"code": "AL"}],
        )

        cls.WORKSPACE_MEMBERSHIP = WorkspaceMembership.objects.create(
            user=cls.USER_JANE,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_notebooks_url(self):
        self.client.force_login(self.USER_JULIA)
        with self.settings(NOTEBOOKS_URL="http://localhost:8081"):
            r = self.run_query(
                """
                query notebooksUrl {
                    notebooksUrl
                }

                """
            )
            self.assertEqual(
                "http://localhost:8081",
                r["data"]["notebooksUrl"],
            )

    def test_launch_workspace_notebook_not_found(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation launchNotebookServer($input: LaunchNotebookServerInput!) {
                launchNotebookServer(input: $input) {
                    success
                    server {
                        name
                        url
                    }
                   errors
                }
            }
            """,
            {"input": {"workspaceSlug": self.WORKSPACE.slug}},
        )
        self.assertEqual(
            {"success": False, "server": None, "errors": ["NOT_FOUND"]},
            r["data"]["launchNotebookServer"],
        )

    def test_launch_workspace_notebook_permission_denied(self):
        self.client.force_login(self.USER_JANE)
        r = self.run_query(
            """
            mutation launchNotebookServer($input: LaunchNotebookServerInput!) {
                launchNotebookServer(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"workspaceSlug": self.WORKSPACE.slug}},
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["launchNotebookServer"],
        )

    @responses.activate
    def test_launch_workspace_notebook_create_user_failed(self):
        with self.settings(NOTEBOOKS_API_URL="http://localhost:8081"):
            self.client.force_login(self.USER_JULIA)
            responses.add(
                responses.GET,
                f"{settings.NOTEBOOKS_API_URL}/users/{self.USER_JULIA.email}",
                json={},
                status=404,
                headers="",
            )
            responses.add(
                responses.POST,
                f"{settings.NOTEBOOKS_API_URL}/users/{self.USER_JULIA.email}",
                json={},
                status=500,
                headers="",
            )
            r = self.run_query(
                """
                mutation launchNotebookServer($input: LaunchNotebookServerInput!) {
                    launchNotebookServer(input: $input) {
                        success
                        errors
                    }
                }
            """,
                {"input": {"workspaceSlug": self.WORKSPACE.slug}},
            )
            self.assertEqual(
                {"success": False, "errors": ["UNKNOWN_ERROR"]},
                r["data"]["launchNotebookServer"],
            )

    @responses.activate
    def test_launch_workspace_notebook_create_server_failed(self):
        with self.settings(NOTEBOOKS_API_URL="http://localhost:8081"):
            self.client.force_login(self.USER_JULIA)
            responses.add(
                responses.GET,
                f"{settings.NOTEBOOKS_API_URL}/users/{self.USER_JULIA.email}",
                json={},
                status=404,
                headers="",
            )
            responses.add(
                responses.POST,
                f"{settings.NOTEBOOKS_API_URL}/users/{self.USER_JULIA.email}",
                json={"servers": []},
                status=201,
                headers="",
            )
            responses.add(
                responses.POST,
                f"{settings.NOTEBOOKS_API_URL}/users/{self.USER_JULIA.email}/servers/{self.WORKSPACE.slug}",
                json={},
                status=500,
                headers="",
            )
            r = self.run_query(
                """
                mutation launchNotebookServer($input: LaunchNotebookServerInput!) {
                    launchNotebookServer(input: $input) {
                        success
                        server {
                            name
                            url
                        }
                        errors
                    }
                }
            """,
                {"input": {"workspaceSlug": self.WORKSPACE.slug}},
            )
            self.assertEqual(
                {"success": False, "server": None, "errors": ["UNKNOWN_ERROR"]},
                r["data"]["launchNotebookServer"],
            )

    @responses.activate
    def test_launch_workspace_notebook(self):
        with self.settings(
            NOTEBOOKS_API_URL="http://localhost:8081",
            NOTEBOOKS_URL="http://localhost:8000",
        ):
            self.client.force_login(self.USER_JULIA)
            responses.add(
                responses.GET,
                f"{settings.NOTEBOOKS_API_URL}/users/{self.USER_JULIA.email}",
                json={},
                status=404,
                headers="",
            )
            responses.add(
                responses.POST,
                f"{settings.NOTEBOOKS_API_URL}/users/{self.USER_JULIA.email}",
                json={"servers": [self.WORKSPACE.slug]},
                status=201,
                headers="",
            )

            r = self.run_query(
                """
                mutation launchNotebookServer($input: LaunchNotebookServerInput!) {
                    launchNotebookServer(input: $input) {
                        success
                        server {
                            name
                            url
                        }
                        errors
                    }
                }
            """,
                {"input": {"workspaceSlug": self.WORKSPACE.slug}},
            )
            self.assertEqual(
                {
                    "success": True,
                    "server": {
                        "name": self.WORKSPACE.slug,
                        "url": f"{settings.NOTEBOOKS_URL}/user/{self.USER_JULIA.email}/{self.WORKSPACE.slug}/",
                    },
                    "errors": [],
                },
                r["data"]["launchNotebookServer"],
            )
