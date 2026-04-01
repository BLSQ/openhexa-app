import json
import uuid
from unittest.mock import MagicMock, patch

from hexa.mcp.tools.webapps import (
    create_static_webapp,
    list_static_webapps,
    update_static_webapp,
)
from hexa.webapps.models import Webapp

from .testutils import MCPTestCase

INITIAL_SHA = "aabbccdd1234567890abcdef1234567890abcdef"


def _mock_forgejo():
    return patch("hexa.git.mixins.get_forgejo_client", return_value=_make_mock_client())


def _make_mock_client():
    client = MagicMock()
    client.get_commits.return_value = [{"id": INITIAL_SHA}]
    client.commit_files.return_value = INITIAL_SHA
    return client


def _unique_name(prefix="Webapp"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


class ListStaticWebappsTest(MCPTestCase):
    @_mock_forgejo()
    def test_list_static_webapps(self, _mock):
        files = [{"path": "index.html", "content": "<html></html>"}]
        create_result = create_static_webapp(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name=_unique_name("List"),
            files_json=json.dumps(files),
        )
        self.assertTrue(create_result["success"], create_result.get("errors"))

        result = list_static_webapps(
            user=self.USER_ADMIN, workspace_slug=self.WORKSPACE.slug
        )
        webapps = result["webapps"]
        self.assertGreaterEqual(webapps["totalItems"], 1)
        slugs = [w["slug"] for w in webapps["items"]]
        self.assertIn(create_result["webapp"]["slug"], slugs)

    def test_list_static_webapps_no_access(self):
        result = list_static_webapps(
            user=self.USER_OUTSIDER, workspace_slug=self.WORKSPACE.slug
        )
        self.assertEqual(result["webapps"]["totalItems"], 0)


class CreateStaticWebappTest(MCPTestCase):
    @_mock_forgejo()
    def test_create_static_webapp(self, _mock):
        files = [{"path": "index.html", "content": "<html><body>Hello</body></html>"}]
        result = create_static_webapp(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name=_unique_name(),
            files_json=json.dumps(files),
        )
        self.assertTrue(result["success"], f"Full result: {result}")
        self.assertEqual(result["webapp"]["type"], "STATIC")

    @_mock_forgejo()
    def test_create_static_webapp_with_multiple_files(self, _mock):
        name = _unique_name()
        files = [
            {"path": "index.html", "content": "<html><body>Hello</body></html>"},
            {"path": "style.css", "content": "body { color: red; }"},
        ]
        result = create_static_webapp(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name=name,
            files_json=json.dumps(files),
        )
        self.assertTrue(result["success"], result.get("errors"))
        webapp = result["webapp"]
        self.assertEqual(webapp["name"], name)
        self.assertEqual(webapp["type"], "STATIC")
        self.assertIn(f"/webapps/{webapp['id']}/", webapp["url"])

    def test_create_static_webapp_invalid_json(self):
        result = create_static_webapp(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name=_unique_name(),
            files_json="not json",
        )
        self.assertEqual(result, {"error": "Invalid JSON in files_json"})

    def test_create_static_webapp_empty_files(self):
        result = create_static_webapp(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name=_unique_name(),
            files_json="[]",
        )
        self.assertEqual(
            result,
            {
                "error": "files_json must be a non-empty JSON array of {path, content} objects"
            },
        )


class UpdateStaticWebappTest(MCPTestCase):
    @_mock_forgejo()
    def test_update_static_webapp_name(self, _mock):
        files = [{"path": "index.html", "content": "<html></html>"}]
        create_result = create_static_webapp(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name=_unique_name("Update"),
            files_json=json.dumps(files),
        )
        self.assertTrue(create_result["success"], create_result.get("errors"))
        webapp_id = str(create_result["webapp"]["id"])

        result = update_static_webapp(
            user=self.USER_ADMIN,
            webapp_id=webapp_id,
            name="Updated Name",
        )
        self.assertTrue(result["success"], result)
        self.assertEqual(result["webapp"]["name"], "Updated Name")
        webapp = Webapp.objects.get(id=webapp_id)
        self.assertEqual(webapp.name, "Updated Name")

    @_mock_forgejo()
    def test_update_static_webapp_files(self, mock_forgejo):
        client = mock_forgejo.return_value
        files = [{"path": "index.html", "content": "<html>old</html>"}]
        create_result = create_static_webapp(
            user=self.USER_ADMIN,
            workspace_slug=self.WORKSPACE.slug,
            name=_unique_name("FileUpd"),
            files_json=json.dumps(files),
        )
        self.assertTrue(create_result["success"], create_result.get("errors"))
        webapp_id = str(create_result["webapp"]["id"])

        client.commit_files.assert_called_once()
        self.assertEqual(client.commit_files.call_args.kwargs["files"], files)
        client.commit_files.reset_mock()

        new_files = [{"path": "index.html", "content": "<html>new</html>"}]
        result = update_static_webapp(
            user=self.USER_ADMIN,
            webapp_id=webapp_id,
            files_json=json.dumps(new_files),
        )
        self.assertTrue(result["success"], result)
        self.assertIn(f"/webapps/{webapp_id}/", result["webapp"]["url"])
        client.commit_files.assert_called_once()
        self.assertEqual(client.commit_files.call_args[0][1], new_files)

    def test_update_static_webapp_invalid_files_json(self):
        result = update_static_webapp(
            user=self.USER_ADMIN,
            webapp_id="00000000-0000-0000-0000-000000000000",
            files_json="not json",
        )
        self.assertEqual(result, {"error": "Invalid JSON in files_json"})
