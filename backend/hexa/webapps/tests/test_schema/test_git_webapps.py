from unittest.mock import MagicMock, patch

from hexa.core.test import GraphQLTestCase
from hexa.git.forgejo import ForgejoAPIError
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

CREATE_WEBAPP_MUTATION = """
    mutation createWebapp($input: CreateWebappInput!) {
        createWebapp(input: $input) {
            success
            errors
            webapp {
                id
                name
                type
                url
            }
        }
    }
"""

UPDATE_WEBAPP_MUTATION = """
    mutation updateWebapp($input: UpdateWebappInput!) {
        updateWebapp(input: $input) {
            success
            errors
            webapp {
                id
                source {
                    ... on GitSource {
                        publishedVersion
                    }
                }
            }
        }
    }
"""

WEBAPP_QUERY = """
    query webapp($workspaceSlug: String!, $slug: String!) {
        webapp(workspaceSlug: $workspaceSlug, slug: $slug) {
            id
            name
            type
            url
            source {
                ... on GitSource {
                    repository
                    publishedVersion
                }
                ... on IframeSource {
                    url
                }
            }
            versions(page: 1, perPage: 10) {
                items {
                    id
                    message
                    authorName
                    authorEmail
                    date
                }
                page
            }
            files {
                id
                name
                path
                type
                content
                parentId
                autoSelect
                language
                lineCount
            }
        }
    }
"""


class GitWebappCreateTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "gitwebapp@test.com",
            "password",
            is_superuser=True,
        )
        cls.WS = Workspace.objects.create(
            name="Git WS",
            slug="git-ws",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WS,
            role=WorkspaceMembershipRole.ADMIN,
        )

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_create_static_webapp(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.create_organization.return_value = {"username": "no-org"}
        mock_client.create_org_repository.return_value = {"name": "webapp-abc"}
        mock_client.get_commits.return_value = [{"id": "auto-init-sha"}]
        mock_client.commit_files.return_value = "sha-initial"
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "My Static App",
                    "workspaceSlug": self.WS.slug,
                    "source": {
                        "static": [
                            {"path": "index.html", "content": "<h1>Hello</h1>"},
                        ]
                    },
                }
            },
        )

        result = response["data"]["createWebapp"]
        self.assertTrue(result["success"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["webapp"]["name"], "My Static App")
        self.assertEqual(result["webapp"]["type"], "STATIC")

        mock_client.create_org_repository.assert_called_once()
        mock_client.commit_files.assert_called_once()

        webapp = GitWebapp.objects.get(pk=result["webapp"]["id"])
        self.assertEqual(webapp.type, Webapp.WebappType.STATIC)
        self.assertTrue(webapp.repository.startswith("git-ws-webapp-"))
        self.assertEqual(webapp.published_commit, "sha-initial")

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_create_static_webapp_empty_files(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.create_organization.return_value = {"username": "no-org"}
        mock_client.create_org_repository.return_value = {"name": "webapp-def"}
        mock_client.get_commits.return_value = [{"id": "initial-static-sha"}]
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "My Empty Static App",
                    "workspaceSlug": self.WS.slug,
                    "source": {"static": []},
                }
            },
        )

        result = response["data"]["createWebapp"]
        self.assertTrue(result["success"])
        self.assertEqual(result["webapp"]["type"], "STATIC")

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_create_static_webapp_permission_denied(self, mock_get_client):
        viewer = User.objects.create_user("gitviewer@test.com", "password")
        WorkspaceMembership.objects.create(
            user=viewer,
            workspace=self.WS,
            role=WorkspaceMembershipRole.VIEWER,
        )

        self.client.force_login(viewer)
        response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "Denied App",
                    "workspaceSlug": self.WS.slug,
                    "source": {"static": [{"path": "index.html", "content": "test"}]},
                }
            },
        )

        result = response["data"]["createWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("PERMISSION_DENIED", result["errors"])
        mock_get_client.assert_not_called()

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_create_static_webapp_url_is_serve_endpoint(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.create_organization.return_value = {}
        mock_client.create_org_repository.return_value = {"name": "webapp-x"}
        mock_client.get_commits.return_value = [{"id": "auto-init-sha"}]
        mock_client.commit_files.return_value = "sha-url-test"
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            CREATE_WEBAPP_MUTATION,
            {
                "input": {
                    "name": "URL Test App",
                    "workspaceSlug": self.WS.slug,
                    "source": {
                        "static": [{"path": "index.html", "content": "<h1>Test</h1>"}]
                    },
                }
            },
        )

        result = response["data"]["createWebapp"]
        self.assertTrue(result["success"])
        webapp_id = result["webapp"]["id"]
        self.assertIn(f"/webapps/{webapp_id}/", result["webapp"]["url"])


class GitWebappUpdateFilesTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "commituser@test.com",
            "password",
        )
        cls.WS = Workspace.objects.create(
            name="Commit WS",
            slug="commit-ws",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WS,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.GIT_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WS,
            name="Commit Test App",
            slug="commit-test-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="webapp-commitrepo",
        )

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_update_files_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.commit_files.return_value = "sha123abc"
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": str(self.GIT_WEBAPP.id),
                    "files": [
                        {"path": "index.html", "content": "<h1>Hello</h1>"},
                        {"path": "style.css", "content": "body { color: red; }"},
                    ],
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertTrue(result["success"])

        self.GIT_WEBAPP.refresh_from_db()
        self.assertEqual(self.GIT_WEBAPP.published_commit, "sha123abc")

        mock_client.commit_files.assert_called_once_with(
            "webapp-commitrepo",
            [
                {"path": "index.html", "content": "<h1>Hello</h1>"},
                {"path": "style.css", "content": "body { color: red; }"},
            ],
            "Update webapp content",
            self.USER.display_name or self.USER.email,
            self.USER.email,
            org_slug="no-org",
        )

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_update_files_permission_denied(self, mock_get_client):
        viewer = User.objects.create_user("commitviewer@test.com", "password")
        WorkspaceMembership.objects.create(
            user=viewer,
            workspace=self.WS,
            role=WorkspaceMembershipRole.VIEWER,
        )

        self.client.force_login(viewer)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": str(self.GIT_WEBAPP.id),
                    "files": [{"path": "index.html", "content": "test"}],
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("PERMISSION_DENIED", result["errors"])
        mock_get_client.assert_not_called()

    def test_update_files_webapp_not_found(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "files": [{"path": "index.html", "content": "test"}],
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("WEBAPP_NOT_FOUND", result["errors"])

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_update_files_forgejo_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.commit_files.side_effect = ForgejoAPIError(
            "POST", "http://forgejo/api", 500, "internal error"
        )
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": str(self.GIT_WEBAPP.id),
                    "files": [{"path": "index.html", "content": "test"}],
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("SAVE_FAILED", result["errors"])


class GitWebappPublishVersionTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "publishuser@test.com",
            "password",
        )
        cls.WS = Workspace.objects.create(
            name="Publish WS",
            slug="publish-ws",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WS,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.GIT_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WS,
            name="Publish Test App",
            slug="publish-test-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="webapp-publishrepo",
        )

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_publish_version_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.commit_exists.return_value = True
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": str(self.GIT_WEBAPP.id),
                    "publishedVersionId": "abc123def456",
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertTrue(result["success"])
        self.assertEqual(result["errors"], [])

        source = result["webapp"]["source"]
        self.assertEqual(source["publishedVersion"], "abc123def456")

        self.GIT_WEBAPP.refresh_from_db()
        self.assertEqual(self.GIT_WEBAPP.published_commit, "abc123def456")

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_publish_version_can_change(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.commit_exists.return_value = True
        mock_get_client.return_value = mock_client

        self.GIT_WEBAPP.published_commit = "old-sha"
        self.GIT_WEBAPP.save()

        self.client.force_login(self.USER)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": str(self.GIT_WEBAPP.id),
                    "publishedVersionId": "new-sha-789",
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertTrue(result["success"])

        self.GIT_WEBAPP.refresh_from_db()
        self.assertEqual(self.GIT_WEBAPP.published_commit, "new-sha-789")

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_publish_version_not_found(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.commit_exists.return_value = False
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": str(self.GIT_WEBAPP.id),
                    "publishedVersionId": "nonexistent-sha",
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("VERSION_NOT_FOUND", result["errors"])

    def test_publish_version_permission_denied(self):
        viewer = User.objects.create_user("publishviewer@test.com", "password")
        WorkspaceMembership.objects.create(
            user=viewer,
            workspace=self.WS,
            role=WorkspaceMembershipRole.VIEWER,
        )

        self.client.force_login(viewer)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": str(self.GIT_WEBAPP.id),
                    "publishedVersionId": "unauthorized",
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("PERMISSION_DENIED", result["errors"])

    def test_publish_version_webapp_not_found(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            UPDATE_WEBAPP_MUTATION,
            {
                "input": {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "publishedVersionId": "not-found",
                }
            },
        )

        result = response["data"]["updateWebapp"]
        self.assertFalse(result["success"])
        self.assertIn("WEBAPP_NOT_FOUND", result["errors"])


class GitWebappQueryTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "queryuser@test.com",
            "password",
        )
        cls.WS = Workspace.objects.create(
            name="Query WS",
            slug="query-ws",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WS,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.GIT_WEBAPP = GitWebapp.objects.create(
            workspace=cls.WS,
            name="Query Test App",
            slug="query-test-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.USER,
            repository="webapp-queryrepo",
            published_commit="published-sha",
        )

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_query_git_webapp_source(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_commits.return_value = []
        mock_client.get_repository_files.return_value = []
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            WEBAPP_QUERY,
            {
                "workspaceSlug": self.WS.slug,
                "slug": "query-test-app",
            },
        )

        webapp = response["data"]["webapp"]
        self.assertIsNotNone(webapp)
        self.assertEqual(webapp["name"], "Query Test App")
        self.assertEqual(webapp["type"], "STATIC")
        self.assertIn(f"/webapps/{self.GIT_WEBAPP.id}/", webapp["url"])
        self.assertEqual(webapp["source"]["repository"], "webapp-queryrepo")
        self.assertEqual(webapp["source"]["publishedVersion"], "published-sha")

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_query_git_webapp_versions(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_commits.return_value = [
            {
                "id": "abc123",
                "message": "initial commit",
                "author_name": "Test User",
                "author_email": "test@example.com",
                "date": "2024-01-01T00:00:00Z",
            },
        ]
        mock_client.get_repository_files.return_value = []
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            WEBAPP_QUERY,
            {
                "workspaceSlug": self.WS.slug,
                "slug": "query-test-app",
            },
        )

        versions = response["data"]["webapp"]["versions"]
        self.assertIsNotNone(versions)
        self.assertEqual(versions["page"], 1)
        self.assertEqual(len(versions["items"]), 1)
        self.assertEqual(versions["items"][0]["id"], "abc123")
        self.assertEqual(versions["items"][0]["message"], "initial commit")
        self.assertEqual(versions["items"][0]["authorName"], "Test User")

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_query_git_webapp_files(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_commits.return_value = []
        mock_client.get_repository_files.return_value = [
            {"path": "index.html", "type": "file", "content": "<h1>Hello</h1>"},
            {"path": "style.css", "type": "file", "content": "body { color: red; }"},
        ]
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            WEBAPP_QUERY,
            {
                "workspaceSlug": self.WS.slug,
                "slug": "query-test-app",
            },
        )

        files = response["data"]["webapp"]["files"]
        self.assertIsNotNone(files)
        self.assertEqual(len(files), 2)

        file_paths = {f["path"] for f in files}
        self.assertIn("index.html", file_paths)
        self.assertIn("style.css", file_paths)

        index_file = next(f for f in files if f["path"] == "index.html")
        self.assertEqual(index_file["name"], "index.html")
        self.assertEqual(index_file["type"], "file")
        self.assertEqual(index_file["content"], "<h1>Hello</h1>")
        self.assertTrue(index_file["autoSelect"])
        self.assertEqual(index_file["language"], "html")

        css_file = next(f for f in files if f["path"] == "style.css")
        self.assertFalse(css_file["autoSelect"])
        self.assertEqual(css_file["language"], "css")

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_query_git_webapp_files_with_directories(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_commits.return_value = []
        mock_client.get_repository_files.return_value = [
            {"path": "assets", "type": "directory", "content": None},
            {"path": "index.html", "type": "file", "content": "<html></html>"},
            {"path": "assets/style.css", "type": "file", "content": "body {}"},
            {
                "path": "assets/script.js",
                "type": "file",
                "content": "console.log('hi');",
            },
        ]
        mock_get_client.return_value = mock_client

        self.client.force_login(self.USER)
        response = self.run_query(
            WEBAPP_QUERY,
            {
                "workspaceSlug": self.WS.slug,
                "slug": "query-test-app",
            },
        )

        files = response["data"]["webapp"]["files"]
        self.assertIsNotNone(files)

        dirs = [f for f in files if f["type"] == "directory"]
        self.assertEqual(len(dirs), 1)
        self.assertEqual(dirs[0]["name"], "assets")
        self.assertEqual(dirs[0]["path"], "assets")
        self.assertIsNone(dirs[0]["parentId"])

        css_file = next(f for f in files if f["path"] == "assets/style.css")
        self.assertEqual(css_file["parentId"], "assets")

    def test_query_iframe_webapp_no_versions(self):
        Webapp.objects.create(
            workspace=self.WS,
            name="Iframe App",
            slug="iframe-app",
            type=Webapp.WebappType.IFRAME,
            created_by=self.USER,
            url="https://example.com",
        )

        self.client.force_login(self.USER)
        response = self.run_query(
            WEBAPP_QUERY,
            {
                "workspaceSlug": self.WS.slug,
                "slug": "iframe-app",
            },
        )

        webapp = response["data"]["webapp"]
        self.assertIsNone(webapp["versions"])
        self.assertIsNone(webapp["files"])


class GitWebappDeleteTest(GraphQLTestCase):
    DELETE_MUTATION = """
        mutation deleteWebapp($input: DeleteWebappInput!) {
            deleteWebapp(input: $input) {
                success
                errors
            }
        }
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "deleteuser@test.com",
            "password",
        )
        cls.WS = Workspace.objects.create(
            name="Delete WS",
            slug="delete-ws",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WS,
            role=WorkspaceMembershipRole.ADMIN,
        )

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_delete_git_webapp(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        git_webapp = GitWebapp.objects.create(
            workspace=self.WS,
            name="To Delete",
            slug="to-delete",
            type=Webapp.WebappType.STATIC,
            created_by=self.USER,
            repository="webapp-todelete",
        )
        webapp_id = str(git_webapp.id)

        self.client.force_login(self.USER)
        response = self.run_query(
            self.DELETE_MUTATION,
            {"input": {"id": webapp_id}},
        )

        result = response["data"]["deleteWebapp"]
        self.assertTrue(result["success"])
        self.assertFalse(Webapp.objects.filter(id=webapp_id).exists())
        mock_client.archive_repository.assert_called_once_with(
            "no-org", "webapp-todelete"
        )
