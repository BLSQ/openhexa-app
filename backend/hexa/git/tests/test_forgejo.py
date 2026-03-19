import base64

import responses
from django.test import TestCase, override_settings

from hexa.git.forgejo import ForgejoAPIError, ForgejoClient, get_forgejo_client

FORGEJO_URL = "http://forgejo-test:3000"
USERNAME = "testuser"
PASSWORD = "testpass"
TOKEN = "abc123tokenvalue"


class ForgejoClientTokenTest(TestCase):
    @responses.activate
    def test_get_or_create_token_creates_new(self):
        responses.get(
            f"{FORGEJO_URL}/api/v1/users/{USERNAME}/tokens",
            json=[],
            status=200,
        )
        responses.post(
            f"{FORGEJO_URL}/api/v1/users/{USERNAME}/tokens",
            json={"id": 1, "name": "openhexa-api", "sha1": TOKEN},
            status=201,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        token = client._get_or_create_token()

        self.assertEqual(token, TOKEN)
        self.assertEqual(len(responses.calls), 2)

    @responses.activate
    def test_get_or_create_token_replaces_existing(self):
        responses.get(
            f"{FORGEJO_URL}/api/v1/users/{USERNAME}/tokens",
            json=[{"id": 42, "name": "test", "sha1": "old-token"}],
            status=200,
        )
        responses.delete(
            f"{FORGEJO_URL}/api/v1/users/{USERNAME}/tokens/42",
            status=204,
        )
        responses.post(
            f"{FORGEJO_URL}/api/v1/users/{USERNAME}/tokens",
            json={"id": 43, "name": "openhexa-api", "sha1": TOKEN},
            status=201,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        token = client._get_or_create_token()

        self.assertEqual(token, TOKEN)
        self.assertEqual(len(responses.calls), 3)

    @responses.activate
    def test_get_or_create_token_error_on_list(self):
        responses.get(
            f"{FORGEJO_URL}/api/v1/users/{USERNAME}/tokens",
            json={"message": "unauthorized"},
            status=401,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        with self.assertRaises(ForgejoAPIError) as ctx:
            client._get_or_create_token()

        self.assertEqual(ctx.exception.status_code, 401)


def _setup_token(forgejo_url=FORGEJO_URL, username=USERNAME):
    responses.get(
        f"{forgejo_url}/api/v1/users/{username}/tokens",
        json=[],
        status=200,
    )
    responses.post(
        f"{forgejo_url}/api/v1/users/{username}/tokens",
        json={"id": 1, "name": "openhexa-api", "sha1": TOKEN},
        status=201,
    )


class ForgejoClientCreateRepositoryTest(TestCase):
    @responses.activate
    def test_create_repository_success(self):
        _setup_token()
        responses.post(
            f"{FORGEJO_URL}/api/v1/user/repos",
            json={"id": 1, "name": "my-repo", "full_name": f"{USERNAME}/my-repo"},
            status=201,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        result = client.create_repository("my-repo")

        self.assertEqual(result["name"], "my-repo")
        post_call = responses.calls[2]
        self.assertIn(b'"auto_init": true', post_call.request.body)

    @responses.activate
    def test_create_repository_already_exists(self):
        _setup_token()
        responses.post(
            f"{FORGEJO_URL}/api/v1/user/repos",
            json={"message": "repository already exists"},
            status=409,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        with self.assertRaises(ForgejoAPIError) as ctx:
            client.create_repository("my-repo")

        self.assertEqual(ctx.exception.status_code, 409)


class ForgejoClientGetFileTest(TestCase):
    @responses.activate
    def test_get_file(self):
        _setup_token()
        content = base64.b64encode(b"hello world").decode()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/contents/README.md",
            json={"content": content, "name": "README.md"},
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        data = client.get_file("my-repo", "README.md")

        self.assertEqual(data, b"hello world")


class ForgejoClientGetFilesTreeTest(TestCase):
    @responses.activate
    def test_get_files_tree(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/git/trees/main",
            json={
                "sha": "abc123",
                "tree": [
                    {"path": "README.md", "type": "blob"},
                    {"path": "src/app.py", "type": "blob"},
                ],
            },
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        tree = client.get_files_tree("my-repo")

        self.assertEqual(len(tree), 2)
        self.assertEqual(tree[0]["path"], "README.md")


class ForgejoClientCommitFilesTest(TestCase):
    @responses.activate
    def test_commit_files_create(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/commits",
            json={"message": "Git Repository is empty."},
            status=409,
        )
        responses.post(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/contents",
            json={"commit": {"sha": "newsha123"}},
            status=201,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        sha = client.commit_files(
            "my-repo",
            [{"path": "hello.txt", "content": "hello"}],
            "initial commit",
            "Test User",
            "test@example.com",
        )

        self.assertEqual(sha, "newsha123")
        post_body = responses.calls[3].request.body
        self.assertIn(b'"operation": "create"', post_body)

    @responses.activate
    def test_commit_files_update(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/commits",
            json=[
                {
                    "sha": "existingsha",
                    "commit": {
                        "message": "previous commit",
                        "author": {
                            "name": "User",
                            "email": "u@example.com",
                            "date": "2024-01-01T00:00:00Z",
                        },
                    },
                }
            ],
            status=200,
        )
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/git/trees/main",
            json={
                "sha": "abc123",
                "tree": [{"path": "hello.txt", "type": "blob"}],
            },
            status=200,
        )
        responses.post(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/contents",
            json={"commit": {"sha": "updatedsha"}},
            status=201,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        sha = client.commit_files(
            "my-repo",
            [{"path": "hello.txt", "content": "updated"}],
            "update file",
            "Test User",
            "test@example.com",
        )

        self.assertEqual(sha, "updatedsha")
        post_body = responses.calls[4].request.body
        self.assertIn(b'"operation": "update"', post_body)


class ForgejoAPIErrorTest(TestCase):
    def test_error_attributes(self):
        error = ForgejoAPIError("GET", "http://example.com/api", 404, "not found")

        self.assertEqual(error.method, "GET")
        self.assertEqual(error.url, "http://example.com/api")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.detail, "not found")
        self.assertIn("404", str(error))

    def test_request_error_propagation(self):
        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        client._token = "fake"
        client._session.headers["Authorization"] = "token fake"

        with responses.RequestsMock() as responses_mock:
            responses_mock.get(
                f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/contents/missing.txt",
                json={"message": "not found"},
                status=404,
            )
            with self.assertRaises(ForgejoAPIError) as ctx:
                client.get_file("my-repo", "missing.txt")

            self.assertEqual(ctx.exception.status_code, 404)
            self.assertEqual(ctx.exception.method, "GET")


class ForgejoClientCreateOrganizationTest(TestCase):
    @responses.activate
    def test_create_organization_success(self):
        _setup_token()
        responses.post(
            f"{FORGEJO_URL}/api/v1/orgs",
            json={"id": 1, "username": "ws-my-workspace"},
            status=201,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        result = client.create_organization("ws-my-workspace", "My Workspace")

        self.assertEqual(result["username"], "ws-my-workspace")

    @responses.activate
    def test_create_organization_already_exists(self):
        _setup_token()
        responses.post(
            f"{FORGEJO_URL}/api/v1/orgs",
            json={"message": "organization already exists"},
            status=409,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        with self.assertRaises(ForgejoAPIError) as ctx:
            client.create_organization("ws-my-workspace", "My Workspace")

        self.assertEqual(ctx.exception.status_code, 409)


class ForgejoClientCreateOrgRepositoryTest(TestCase):
    @responses.activate
    def test_create_org_repository_success(self):
        _setup_token()
        responses.post(
            f"{FORGEJO_URL}/api/v1/orgs/ws-myworkspace/repos",
            json={
                "id": 1,
                "name": "webapp-abc123",
                "full_name": "ws-myworkspace/webapp-abc123",
            },
            status=201,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        result = client.create_org_repository("ws-myworkspace", "webapp-abc123")

        self.assertEqual(result["name"], "webapp-abc123")

    @responses.activate
    def test_create_org_repository_already_exists(self):
        _setup_token()
        responses.post(
            f"{FORGEJO_URL}/api/v1/orgs/ws-myworkspace/repos",
            json={"message": "repository already exists"},
            status=409,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        with self.assertRaises(ForgejoAPIError) as ctx:
            client.create_org_repository("ws-myworkspace", "webapp-abc123")

        self.assertEqual(ctx.exception.status_code, 409)


class ForgejoClientArchiveRepositoryTest(TestCase):
    @responses.activate
    def test_archive_repository(self):
        _setup_token()
        responses.patch(
            f"{FORGEJO_URL}/api/v1/repos/ws-myworkspace/webapp-abc123",
            json={"name": "webapp-abc123", "archived": True},
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        result = client.archive_repository("ws-myworkspace", "webapp-abc123")

        self.assertTrue(result["archived"])


class ForgejoClientGetFilesTreeWithOwnerTest(TestCase):
    @responses.activate
    def test_get_files_tree_with_owner(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/ws-myworkspace/my-repo/git/trees/main",
            json={
                "sha": "abc123",
                "tree": [
                    {"path": "index.html", "type": "blob"},
                    {"path": "style.css", "type": "blob"},
                ],
            },
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        tree = client.get_files_tree("my-repo", org_slug="ws-myworkspace")

        self.assertEqual(len(tree), 2)
        self.assertEqual(tree[0]["path"], "index.html")

    @responses.activate
    def test_get_files_tree_defaults_to_username(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/git/trees/main",
            json={"sha": "abc", "tree": [{"path": "file.txt", "type": "blob"}]},
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        tree = client.get_files_tree("my-repo")

        self.assertEqual(len(tree), 1)


class ForgejoClientGetFileWithOwnerTest(TestCase):
    @responses.activate
    def test_get_file_with_owner(self):
        _setup_token()
        content = base64.b64encode(b"<h1>Hello</h1>").decode()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/ws-myworkspace/my-repo/contents/index.html",
            json={"content": content, "name": "index.html"},
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        data = client.get_file("my-repo", "index.html", org_slug="ws-myworkspace")

        self.assertEqual(data, b"<h1>Hello</h1>")


class ForgejoClientCommitFilesWithOwnerTest(TestCase):
    @responses.activate
    def test_commit_files_with_owner(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/ws-myworkspace/my-repo/commits",
            json={"message": "Git Repository is empty."},
            status=409,
        )
        responses.post(
            f"{FORGEJO_URL}/api/v1/repos/ws-myworkspace/my-repo/contents",
            json={"commit": {"sha": "newsha456"}},
            status=201,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        sha = client.commit_files(
            "my-repo",
            [{"path": "index.html", "content": "<h1>Hello</h1>"}],
            "initial commit",
            "Test User",
            "test@example.com",
            org_slug="ws-myworkspace",
        )

        self.assertEqual(sha, "newsha456")
        post_call = responses.calls[3]
        self.assertIn(b'"operation": "create"', post_call.request.body)
        self.assertIn("/repos/ws-myworkspace/my-repo/contents", post_call.request.url)


class ForgejoClientGetCommitsTest(TestCase):
    @responses.activate
    def test_get_commits(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/ws-myworkspace/my-repo/commits",
            json=[
                {
                    "sha": "abc123",
                    "commit": {
                        "message": "initial commit",
                        "author": {
                            "name": "Test User",
                            "email": "test@example.com",
                            "date": "2024-01-01T00:00:00Z",
                        },
                    },
                },
                {
                    "sha": "def456",
                    "commit": {
                        "message": "second commit",
                        "author": {
                            "name": "Other User",
                            "email": "other@example.com",
                            "date": "2024-01-02T00:00:00Z",
                        },
                    },
                },
            ],
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        commits = client.get_commits("ws-myworkspace", "my-repo")

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]["id"], "abc123")
        self.assertEqual(commits[0]["message"], "initial commit")

    @responses.activate
    def test_get_commits_with_pagination(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/ws-myworkspace/my-repo/commits",
            json=[
                {
                    "sha": "abc",
                    "commit": {
                        "message": "msg",
                        "author": {
                            "name": "u",
                            "email": "e",
                            "date": "2024-01-01T00:00:00Z",
                        },
                    },
                }
            ],
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        client.get_commits("ws-myworkspace", "my-repo", page=2, limit=5)

        get_call = responses.calls[2]
        self.assertIn("page=2", get_call.request.url)
        self.assertIn("limit=5", get_call.request.url)


class ForgejoClientListOrgRepositoriesTest(TestCase):
    @responses.activate
    def test_list_org_repositories(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/orgs/org-abc123/repos",
            json=[
                {"name": "repo-1", "archived": False},
                {"name": "repo-2", "archived": True},
            ],
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        repos = client.list_org_repositories("org-abc123")

        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]["name"], "repo-1")
        self.assertEqual(repos[1]["name"], "repo-2")

    @responses.activate
    def test_list_org_repositories_with_pagination(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/orgs/org-abc123/repos",
            json=[{"name": "repo-1", "archived": False}],
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        client.list_org_repositories("org-abc123", page=2, limit=10)

        get_call = responses.calls[2]
        self.assertIn("page=2", get_call.request.url)
        self.assertIn("limit=10", get_call.request.url)

    @responses.activate
    def test_list_org_repositories_not_found(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/orgs/org-missing/repos",
            json={"message": "not found"},
            status=404,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        with self.assertRaises(ForgejoAPIError) as ctx:
            client.list_org_repositories("org-missing")

        self.assertEqual(ctx.exception.status_code, 404)


class ForgejoClientUnarchiveRepositoryTest(TestCase):
    @responses.activate
    def test_unarchive_repository(self):
        _setup_token()
        responses.patch(
            f"{FORGEJO_URL}/api/v1/repos/org-abc123/webapp-1",
            json={"name": "webapp-1", "archived": False},
            status=200,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        result = client.unarchive_repository("org-abc123", "webapp-1")

        self.assertFalse(result["archived"])

    @responses.activate
    def test_unarchive_repository_not_found(self):
        _setup_token()
        responses.patch(
            f"{FORGEJO_URL}/api/v1/repos/org-abc123/missing-repo",
            json={"message": "not found"},
            status=404,
        )

        client = ForgejoClient(
            url=FORGEJO_URL,
            username=USERNAME,
            password=PASSWORD,
            application_name="test",
        )
        with self.assertRaises(ForgejoAPIError) as ctx:
            client.unarchive_repository("org-abc123", "missing-repo")

        self.assertEqual(ctx.exception.status_code, 404)


class ForgejoClientGetForgejoClientTest(TestCase):
    @override_settings(
        GIT_SERVER_URL="http://test-forgejo:3000",
        GIT_SERVER_ADMIN_USERNAME="admin",
        GIT_SERVER_ADMIN_PASSWORD="secret",
    )
    def test_get_forgejo_client(self):
        import hexa.git.forgejo as forgejo_module

        forgejo_module._forgejo_client = None
        client = get_forgejo_client()

        self.assertIsInstance(client, ForgejoClient)
        self.assertEqual(client._url, "http://test-forgejo:3000")
        self.assertEqual(client._username, "admin")
        self.assertEqual(client._password, "secret")

        forgejo_module._forgejo_client = None
