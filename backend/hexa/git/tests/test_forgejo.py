import base64

import responses
from django.test import TestCase

from hexa.git.forgejo import ForgejoAPIError, ForgejoClient

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

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
        token = client._get_or_create_token()

        self.assertEqual(token, TOKEN)
        self.assertEqual(len(responses.calls), 2)

    @responses.activate
    def test_get_or_create_token_replaces_existing(self):
        responses.get(
            f"{FORGEJO_URL}/api/v1/users/{USERNAME}/tokens",
            json=[{"id": 42, "name": "openhexa-api", "sha1": "old-token"}],
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

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
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

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
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

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
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
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo",
            json={"id": 1, "name": "my-repo", "full_name": f"{USERNAME}/my-repo"},
            status=200,
        )

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
        result = client.create_repository("my-repo")

        self.assertEqual(result["name"], "my-repo")


class ForgejoClientDeleteRepositoryTest(TestCase):
    @responses.activate
    def test_delete_repository_success(self):
        _setup_token()
        responses.delete(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo",
            status=204,
        )

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
        client.delete_repository("my-repo")

        self.assertEqual(len(responses.calls), 3)  # 2 for token setup + 1 DELETE

    @responses.activate
    def test_delete_repository_not_found(self):
        _setup_token()
        responses.delete(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo",
            json={"message": "not found"},
            status=404,
        )

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
        client.delete_repository("my-repo")  # Should not raise

        self.assertEqual(len(responses.calls), 3)  # 2 for token setup + 1 DELETE


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

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
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

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
        tree = client.get_files_tree("my-repo")

        self.assertEqual(len(tree), 2)
        self.assertEqual(tree[0]["path"], "README.md")


class ForgejoClientCommitFilesTest(TestCase):
    @responses.activate
    def test_commit_files_create(self):
        _setup_token()
        responses.get(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/git/trees/main",
            json={"sha": "abc123", "tree": []},
            status=200,
        )
        responses.post(
            f"{FORGEJO_URL}/api/v1/repos/{USERNAME}/my-repo/contents",
            json={"commit": {"sha": "newsha123"}},
            status=201,
        )

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
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

        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
        sha = client.commit_files(
            "my-repo",
            [{"path": "hello.txt", "content": "updated"}],
            "update file",
            "Test User",
            "test@example.com",
        )

        self.assertEqual(sha, "updatedsha")
        post_body = responses.calls[3].request.body
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
        client = ForgejoClient(url=FORGEJO_URL, username=USERNAME, password=PASSWORD)
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
