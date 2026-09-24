from unittest.mock import MagicMock, patch

import httpx
from django.test import SimpleTestCase

from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.webapps import (
    NOT_COPIED_NOTE,
    VERSIONS_PAGE_SIZE,
    WebappsCopier,
)
from hexa.workspace_copier.results import CopyResult, format_summary
from hexa.workspace_copier.transport import GraphQLError


def _file(path, content, encoding="TEXT", **overrides):
    node = {
        "path": path,
        "type": "file",
        "content": content,
        "encoding": encoding,
        "tooLarge": False,
    }
    node.update(overrides)
    return node


def _webapp(slug, type_="STATIC", **overrides):
    webapp = {
        "id": f"id-{slug}",
        "slug": slug,
        "name": slug.title(),
        "description": "desc",
        "type": type_,
        "icon": None,
        "isPublic": True,
        "allowedOperations": ["FILES_READ"],
        "source": {"__typename": "GitSource", "publishedVersion": None},
    }
    webapp.update(overrides)
    return webapp


class FakeServers:
    """Routes the copier's ``gql`` calls to an in-memory source and target.

    ``commits`` maps a source web app slug to its history, oldest first, as
    ``[(sha, message, [file nodes]), ...]``. Every target write is recorded in
    ``calls`` and gets a fresh ``t-<n>`` sha, like a real git server would.
    ``fail_on(operation_name, input)`` may return an exception to raise instead.
    """

    def __init__(self, source_webapps, commits, target_webapps=(), commit_message=True):
        self.source_client = MagicMock(name="source")
        self.target_client = MagicMock(name="target")
        self.source_webapps = source_webapps
        self.commits = commits
        self.target_webapps = list(target_webapps)
        self.commit_message = commit_message
        self.calls = []
        self.fail_on = lambda operation_name, input_: None
        self._sha = 0

    def _next_sha(self):
        self._sha += 1
        return f"t-{self._sha}"

    def __call__(self, client, query, variables=None, operation_name=None):
        variables = variables or {}
        is_source = client is self.source_client
        if operation_name == "ListWorkspaceWebapps":
            items = self.source_webapps if is_source else self.target_webapps
            return {"webapps": {"totalPages": 1, "items": items}}
        if operation_name == "WebappVersions":
            history = self.commits[variables["slug"]][::-1]
            start = (variables["page"] - 1) * variables["perPage"]
            items = [
                {"id": sha, "message": msg}
                for sha, msg, _ in history[start : start + variables["perPage"]]
            ]
            return {"webapp": {"versions": {"items": items}}}
        if operation_name == "WebappFiles":
            files = {sha: nodes for sha, _, nodes in self.commits[variables["slug"]]}[
                variables["ref"]
            ]
            return {"webapp": {"files": files}}
        if operation_name == "UpdateWebappInputFields":
            names = ["id", "files"] + (["commitMessage"] if self.commit_message else [])
            return {"__type": {"inputFields": [{"name": n} for n in names]}}

        self.calls.append((operation_name, variables["input"]))
        error = self.fail_on(operation_name, variables["input"])
        if error is not None:
            raise error
        if operation_name == "CreateWebapp":
            slug = variables["input"]["name"].lower()
            return {
                "createWebapp": {
                    "success": True,
                    "errors": [],
                    "webapp": {
                        "id": f"target-{slug}",
                        "slug": slug,
                        "source": {"publishedVersion": self._next_sha()},
                    },
                }
            }
        if operation_name == "UpdateWebapp":
            input_ = variables["input"]
            sha = input_.get("publishedVersionId") or self._next_sha()
            return {
                "updateWebapp": {
                    "success": True,
                    "errors": [],
                    "webapp": {"source": {"publishedVersion": sha}},
                }
            }
        if operation_name == "DeleteWebapp":
            return {"deleteWebapp": {"success": True, "errors": []}}
        raise AssertionError(f"unexpected operation {operation_name}")

    def writes(self, operation_name):
        return [input_ for op, input_ in self.calls if op == operation_name]


class WebappsCopierRemoteTest(SimpleTestCase):
    def run_copy(self, servers):
        result = CopyResult()
        source = Endpoint.remote(servers.source_client, "src")
        target = Endpoint.remote(servers.target_client, "tgt")
        with patch("hexa.workspace_copier.resources.webapps.gql", servers):
            WebappsCopier().copy(source, target, result, NullReporter())
        return result

    def test_static_history_is_replayed_as_diffs(self):
        servers = FakeServers(
            [_webapp("app", source={"publishedVersion": "s3"})],
            {
                "app": [
                    ("s1", "Initial content", [_file("index.html", "v1")]),
                    (
                        "s2",
                        "Add style",
                        [
                            _file("index.html", "v1"),
                            _file("style.css", "body{}"),
                            _file("logo.png", "iVBO", encoding="BASE64"),
                        ],
                    ),
                    (
                        "s3",
                        "Drop style",
                        [
                            _file("index.html", "v2"),
                            _file("logo.png", "iVBO", encoding="BASE64"),
                        ],
                    ),
                ]
            },
        )

        result = self.run_copy(servers)

        [create] = servers.writes("CreateWebapp")
        self.assertEqual(
            create["source"],
            {"static": [{"path": "index.html", "content": "v1", "encoding": "TEXT"}]},
        )
        self.assertEqual(create["name"], "App")
        self.assertEqual(create["allowedOperations"], ["FILES_READ"])
        self.assertTrue(create["isPublic"])

        second, third = servers.writes("UpdateWebapp")
        self.assertEqual(
            second,
            {
                "id": "target-app",
                "files": [
                    {"path": "logo.png", "content": "iVBO", "encoding": "BASE64"},
                    {"path": "style.css", "content": "body{}", "encoding": "TEXT"},
                ],
                "filesToDelete": [],
                "commitMessage": "Add style",
            },
        )
        self.assertEqual(
            third,
            {
                "id": "target-app",
                "files": [{"path": "index.html", "content": "v2", "encoding": "TEXT"}],
                "filesToDelete": ["style.css"],
                "commitMessage": "Drop style",
            },
        )
        self.assertEqual(result.webapps.created, [("app", 3)])
        self.assertEqual(result.webapps.failed, [])

    def test_published_version_older_than_latest_is_republished(self):
        servers = FakeServers(
            [_webapp("app", source={"publishedVersion": "s1"})],
            {
                "app": [
                    ("s1", "Initial content", [_file("index.html", "v1")]),
                    ("s2", "Edit", [_file("index.html", "v2")]),
                ]
            },
        )

        self.run_copy(servers)

        # t-1 is the target commit created from s1.
        self.assertEqual(
            servers.writes("UpdateWebapp")[-1],
            {"id": "target-app", "publishedVersionId": "t-1"},
        )

    def test_latest_published_version_needs_no_extra_publish(self):
        servers = FakeServers(
            [_webapp("app", source={"publishedVersion": "s2"})],
            {
                "app": [
                    ("s1", "Initial content", [_file("index.html", "v1")]),
                    ("s2", "Edit", [_file("index.html", "v2")]),
                ]
            },
        )

        self.run_copy(servers)

        self.assertFalse(
            any("publishedVersionId" in w for w in servers.writes("UpdateWebapp"))
        )

    def test_commit_without_changes_is_still_recreated(self):
        servers = FakeServers(
            [_webapp("app", source={"publishedVersion": "s2"})],
            {
                "app": [
                    ("s1", "Initial content", [_file("index.html", "v1")]),
                    ("s2", "Saved again", [_file("index.html", "v1")]),
                    ("s3", "Edit", [_file("index.html", "v3")]),
                ]
            },
        )

        result = self.run_copy(servers)

        resave, _edit, publish = servers.writes("UpdateWebapp")
        self.assertEqual(
            resave,
            {
                "id": "target-app",
                "files": [{"path": "index.html", "content": "v1", "encoding": "TEXT"}],
                "filesToDelete": [],
                "commitMessage": "Saved again",
            },
        )
        self.assertEqual(publish, {"id": "target-app", "publishedVersionId": "t-2"})
        self.assertEqual(result.webapps.created, [("app", 3)])

    def test_commit_without_files_is_counted_as_not_recreated(self):
        servers = FakeServers(
            [_webapp("app")],
            {"app": [("s1", "Initial", []), ("s2", "Empty", [])]},
        )

        result = self.run_copy(servers)

        self.assertEqual(servers.writes("UpdateWebapp"), [])
        self.assertEqual(result.webapps.created, [("app", 1)])
        self.assertTrue(any("fewer versions" in w for w in result.webapps.warnings))

    def test_every_version_page_is_read(self):
        history = [
            (f"s{i}", f"commit {i}", [_file("index.html", str(i))])
            for i in range(VERSIONS_PAGE_SIZE + 2)
        ]
        servers = FakeServers([_webapp("app")], {"app": history})

        result = self.run_copy(servers)

        self.assertEqual(result.webapps.created, [("app", VERSIONS_PAGE_SIZE + 2)])
        self.assertEqual(len(servers.writes("UpdateWebapp")), VERSIONS_PAGE_SIZE + 1)

    def test_commit_message_omitted_when_target_does_not_support_it(self):
        servers = FakeServers(
            [_webapp("app")],
            {
                "app": [
                    ("s1", "Initial content", [_file("index.html", "v1")]),
                    ("s2", "Edit", [_file("index.html", "v2")]),
                ]
            },
            commit_message=False,
        )

        result = self.run_copy(servers)

        self.assertNotIn("commitMessage", servers.writes("UpdateWebapp")[0])
        self.assertTrue(any("commit messages" in w for w in result.webapps.warnings))

    def test_iframe_webapp_is_created_from_its_url(self):
        servers = FakeServers(
            [
                _webapp(
                    "embed",
                    type_="IFRAME",
                    source={"__typename": "IframeSource", "url": "https://x.org"},
                )
            ],
            {},
        )

        result = self.run_copy(servers)

        [create] = servers.writes("CreateWebapp")
        self.assertEqual(create["source"], {"iframe": {"url": "https://x.org"}})
        self.assertEqual(result.webapps.created, [("embed", 0)])
        self.assertIn(NOT_COPIED_NOTE, result.webapps.warnings)

    def test_superset_webapp_is_skipped_with_warning(self):
        servers = FakeServers(
            [
                _webapp(
                    "dash",
                    type_="SUPERSET",
                    source={
                        "__typename": "SupersetSource",
                        "dashboardId": "42",
                        "instance": {"name": "BI", "url": "https://bi.org"},
                    },
                )
            ],
            {},
        )

        result = self.run_copy(servers)

        self.assertEqual(servers.calls, [])
        self.assertEqual(result.webapps.skipped, ["dash"])
        self.assertTrue(any("dashboard 42" in w for w in result.webapps.warnings))

    def test_existing_webapp_is_skipped_by_name(self):
        servers = FakeServers(
            [_webapp("app")],
            {"app": [("s1", "Initial", [_file("index.html", "v1")])]},
            target_webapps=[_webapp("app-ab12", name="App")],
        )

        result = self.run_copy(servers)

        self.assertEqual(servers.calls, [])
        self.assertEqual(result.webapps.skipped, ["app"])

    def test_too_large_file_fails_before_anything_is_created(self):
        servers = FakeServers(
            [_webapp("app"), _webapp("other")],
            {
                "app": [
                    (
                        "s1",
                        "Initial",
                        [_file("big.bin", None, encoding="BASE64", tooLarge=True)],
                    )
                ],
                "other": [("o1", "Initial", [_file("index.html", "v1")])],
            },
        )

        result = self.run_copy(servers)

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertEqual(result.webapps.created, [("other", 1)])
        self.assertEqual([c["name"] for c in servers.writes("CreateWebapp")], ["Other"])

    def test_failed_replay_deletes_the_partial_target_webapp(self):
        servers = FakeServers(
            [_webapp("app")],
            {
                "app": [
                    ("s1", "Initial", [_file("index.html", "v1")]),
                    ("s2", "Edit", [_file("index.html", "v2")]),
                ]
            },
        )
        servers.fail_on = lambda op, input_: (
            GraphQLError("boom") if op == "UpdateWebapp" else None
        )

        result = self.run_copy(servers)

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertEqual(servers.writes("DeleteWebapp"), [{"id": "target-app"}])

    def test_timeout_fails_one_webapp_and_the_next_is_copied(self):
        servers = FakeServers(
            [_webapp("app"), _webapp("other")],
            {
                "app": [
                    ("s1", "Initial", [_file("index.html", "v1")]),
                    ("s2", "Edit", [_file("index.html", "v2")]),
                ],
                "other": [("o1", "Initial", [_file("index.html", "v1")])],
            },
        )
        servers.fail_on = lambda op, input_: (
            httpx.ReadTimeout("timed out") if op == "UpdateWebapp" else None
        )

        result = self.run_copy(servers)

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertEqual(result.webapps.created, [("other", 1)])
        self.assertEqual(servers.writes("DeleteWebapp"), [{"id": "target-app"}])

    def test_unmatched_published_version_is_reported_as_incomplete(self):
        servers = FakeServers(
            [_webapp("app", source={"publishedVersion": "off-main"})],
            {
                "app": [
                    ("s1", "Initial", [_file("index.html", "v1")]),
                    ("s2", "Edit", [_file("index.html", "v2")]),
                ]
            },
        )

        result = self.run_copy(servers)

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertEqual(result.webapps.created, [])
        # The replayed history is kept: only the publishing is left to do.
        self.assertEqual(servers.writes("DeleteWebapp"), [])
        self.assertTrue(
            any("off-main" in w and "incomplete" in w for w in result.webapps.warnings)
        )

    def test_failed_publish_keeps_the_webapp_and_reports_it_incomplete(self):
        servers = FakeServers(
            [_webapp("app", source={"publishedVersion": "s1"})],
            {
                "app": [
                    ("s1", "Initial", [_file("index.html", "v1")]),
                    ("s2", "Edit", [_file("index.html", "v2")]),
                ]
            },
        )
        servers.fail_on = lambda op, input_: (
            GraphQLError("VERSION_NOT_FOUND")
            if "publishedVersionId" in input_
            else None
        )

        result = self.run_copy(servers)

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertEqual(servers.writes("DeleteWebapp"), [])
        self.assertTrue(any("incomplete" in w for w in result.webapps.warnings))

    def test_summary_lists_webapps(self):
        servers = FakeServers(
            [_webapp("app")],
            {"app": [("s1", "Initial", [_file("index.html", "v1")])]},
        )

        summary = format_summary(self.run_copy(servers))

        self.assertIn("Web apps created: 1", summary)
        self.assertIn("  * app (1 version(s))", summary)

    def test_local_endpoint_not_yet_implemented(self):
        with self.assertRaises(NotImplementedError):
            WebappsCopier().copy(
                Endpoint.local("src"),
                Endpoint.remote(MagicMock(), "tgt"),
                CopyResult(),
                NullReporter(),
            )
