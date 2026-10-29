from unittest.mock import MagicMock, patch

import httpx
from django.db import IntegrityError
from django.test import SimpleTestCase

from hexa.core.test import TestCase
from hexa.git.forgejo import ForgejoAPIError
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, Webapp
from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.webapps import (
    MIGRATION_REFUSED_HINT,
    NOT_COPIED_NOTE,
    NOT_ON_THIS_SERVER_WARNING,
    STATIC_ACROSS_SERVERS_WARNING,
    WebappsCopier,
)
from hexa.workspace_copier.results import CopyResult, format_summary
from hexa.workspace_copier.transport import GraphQLError
from hexa.workspaces.tests.testutils import create_workspace


def _webapp(slug, type_="IFRAME", **overrides):
    webapp = {
        "id": f"id-{slug}",
        "slug": slug,
        "name": slug.title(),
        "description": "desc",
        "type": type_,
        "icon": None,
        "isPublic": True,
        "allowedOperations": ["FILES_READ"],
        "source": {"__typename": "IframeSource", "url": f"https://{slug}.org"},
    }
    webapp.update(overrides)
    return webapp


class FakeServers:
    """Routes the copier's ``gql`` calls to an in-memory source and target.

    Every target write is recorded in ``calls``; ``fail_on(input)`` may return an
    exception to raise instead.
    """

    def __init__(self, source_webapps, target_webapps=()):
        self.source_client = MagicMock(name="source")
        self.target_client = MagicMock(name="target")
        self.source_webapps = source_webapps
        self.target_webapps = list(target_webapps)
        self.calls = []
        self.fail_on = lambda input_: None

    def __call__(self, client, query, variables=None, operation_name=None):
        if operation_name == "ListWorkspaceWebapps":
            is_source = client is self.source_client
            items = self.source_webapps if is_source else self.target_webapps
            return {"webapps": {"totalPages": 1, "items": items}}
        if operation_name == "CreateWebapp":
            input_ = variables["input"]
            self.calls.append(input_)
            error = self.fail_on(input_)
            if error is not None:
                raise error
            return {
                "createWebapp": {
                    "success": True,
                    "errors": [],
                    "webapp": {"slug": input_["name"].lower()},
                }
            }
        raise AssertionError(f"unexpected operation {operation_name}")


class WebappsCopierAcrossServersTest(SimpleTestCase):
    def run_copy(self, servers):
        result = CopyResult()
        source = Endpoint(servers.source_client, "src")
        target = Endpoint(servers.target_client, "tgt")
        with patch("hexa.workspace_copier.resources.webapps.gql", servers):
            WebappsCopier().copy(source, target, result, NullReporter())
        return result

    def test_iframe_webapp_is_created_from_its_url(self):
        servers = FakeServers([_webapp("embed")])

        result = self.run_copy(servers)

        [create] = servers.calls
        self.assertEqual(create["source"], {"iframe": {"url": "https://embed.org"}})
        self.assertEqual(result.webapps.created, ["embed"])
        self.assertIn(NOT_COPIED_NOTE, result.webapps.warnings)

    def test_static_webapp_is_skipped_across_servers(self):
        servers = FakeServers(
            [
                _webapp(
                    "app",
                    type_="STATIC",
                    source={"__typename": "GitSource"},
                )
            ]
        )

        result = self.run_copy(servers)

        self.assertEqual(servers.calls, [])
        self.assertEqual(result.webapps.skipped, ["app"])
        self.assertIn(
            STATIC_ACROSS_SERVERS_WARNING.format(slug="app"), result.webapps.warnings
        )

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
            ]
        )

        result = self.run_copy(servers)

        self.assertEqual(servers.calls, [])
        self.assertEqual(result.webapps.skipped, ["dash"])
        self.assertTrue(any("dashboard 42" in w for w in result.webapps.warnings))

    def test_existing_webapp_is_skipped_by_name(self):
        servers = FakeServers(
            [_webapp("app")], target_webapps=[_webapp("app-ab12", name="App")]
        )

        result = self.run_copy(servers)

        self.assertEqual(servers.calls, [])
        self.assertEqual(result.webapps.skipped, ["app"])

    def test_timeout_fails_one_webapp_and_the_next_is_copied(self):
        servers = FakeServers([_webapp("app"), _webapp("other")])
        servers.fail_on = lambda input_: (
            httpx.ReadTimeout("timed out") if input_["name"] == "App" else None
        )

        result = self.run_copy(servers)

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertEqual(result.webapps.created, ["other"])

    def test_failed_create_is_reported(self):
        servers = FakeServers([_webapp("app")])
        servers.fail_on = lambda input_: GraphQLError("boom")

        result = self.run_copy(servers)

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertTrue(any("boom" in w for w in result.webapps.warnings))

    def test_summary_lists_webapps(self):
        summary = format_summary(self.run_copy(FakeServers([_webapp("app")])))

        self.assertIn("Web apps created: 1", summary)
        self.assertIn("  * app", summary)


def _static_listing(*slugs):
    return [
        _webapp(slug, type_="STATIC", source={"__typename": "GitSource"})
        for slug in slugs
    ]


class WebappsCopierSameServerTest(TestCase):
    PUBLISHED_SHA = "aabbccdd1234567890abcdef1234567890abcdef"

    def setUp(self):
        patcher = patch("hexa.git.mixins.get_forgejo_client")
        self.git = MagicMock()
        self.git.get_repository.return_value = {"private": True}
        patcher.start().return_value = self.git
        self.addCleanup(patcher.stop)

        self.author = User.objects.create_user("author@bluesquarehub.com", "pw")
        self.source_ws = create_workspace(name="Source", slug="source", db_name="src")
        self.target_ws = create_workspace(name="Target", slug="target", db_name="tgt")

    def run_copy(self, servers, target_slug="target"):
        result = CopyResult()
        with patch("hexa.workspace_copier.resources.webapps.gql", servers):
            WebappsCopier().copy(
                Endpoint(servers.source_client, "source"),
                Endpoint(servers.target_client, target_slug),
                result,
                NullReporter(),
                options=CopyOptions(same_server=True),
            )
        return result

    def _static(self, slug):
        return GitWebapp.objects.create(
            workspace=self.source_ws,
            type=Webapp.WebappType.STATIC,
            name=slug.title(),
            slug=slug,
            subdomain=f"source-{slug}",
            description="desc",
            is_public=True,
            allowed_operations=["FILES_READ"],
            created_by=self.author,
            repository=f"source-webapp-{slug}",
            published_commit=self.PUBLISHED_SHA,
        )

    def test_static_webapp_is_copied_with_its_repository(self):
        source = self._static("app")
        servers = FakeServers(_static_listing("app"))

        result = self.run_copy(servers)

        copy = GitWebapp.objects.get(workspace=self.target_ws)
        self.assertEqual(result.webapps.created, [copy.slug])
        self.assertEqual(copy.name, "App")
        self.assertEqual(copy.type, Webapp.WebappType.STATIC)
        self.assertEqual(copy.repository, f"target-webapp-{copy.slug}")
        self.assertEqual(copy.published_commit, self.PUBLISHED_SHA)
        self.assertEqual(copy.created_by, self.author)
        self.assertEqual(copy.description, "desc")
        self.assertTrue(copy.is_public)
        self.assertEqual(copy.allowed_operations, ["FILES_READ"])
        self.assertNotEqual(copy.subdomain, source.subdomain)
        self.git.migrate_repository.assert_called_once_with(
            source_org_slug=self.source_ws.organization.slug,
            source_repo_name=source.repository,
            target_org_slug=self.target_ws.organization.slug,
            target_repo_name=copy.repository,
            private=True,
        )
        self.git.protect_branch.assert_called_once_with(
            self.target_ws.organization.slug, copy.repository
        )
        self.assertEqual(servers.calls, [])

    def test_iframe_webapp_still_goes_through_graphql(self):
        servers = FakeServers([_webapp("embed")])

        result = self.run_copy(servers)

        [create] = servers.calls
        self.assertEqual(create["source"], {"iframe": {"url": "https://embed.org"}})
        self.assertEqual(result.webapps.created, ["embed"])
        self.git.migrate_repository.assert_not_called()

    def test_workspace_not_on_this_server_fails_static_webapps(self):
        self._static("app")
        servers = FakeServers(_static_listing("app") + [_webapp("embed")])

        result = self.run_copy(servers, target_slug="on-another-server")

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertEqual(result.webapps.created, ["embed"])
        self.assertIn(
            NOT_ON_THIS_SERVER_WARNING.format(slug="app"), result.webapps.warnings
        )
        self.git.migrate_repository.assert_not_called()

    def test_failed_migration_fails_one_webapp_and_the_next_is_copied(self):
        self._static("broken")
        self._static("fine")
        self.git.migrate_repository.side_effect = [
            ForgejoAPIError("POST", "/api/v1/repos/migrate", 500, "server error"),
            {},
        ]

        result = self.run_copy(FakeServers(_static_listing("broken", "fine")))

        self.assertEqual(result.webapps.failed, ["broken"])
        self.assertEqual(result.webapps.created, ["fine"])
        self.assertEqual(
            list(
                GitWebapp.objects.filter(workspace=self.target_ws).values_list(
                    "name", flat=True
                )
            ),
            ["Fine"],
        )
        self.git.delete_repository.assert_not_called()

    def test_refused_migration_names_the_forgejo_setting(self):
        self._static("app")
        self.git.migrate_repository.side_effect = ForgejoAPIError(
            "POST",
            "http://forgejo:3000/api/v1/repos/migrate",
            422,
            '{"message":"You can not import from disallowed hosts."}',
        )

        result = self.run_copy(FakeServers(_static_listing("app")))

        self.assertEqual(result.webapps.failed, ["app"])
        self.assertTrue(result.has_failures)
        self.assertTrue(
            any(MIGRATION_REFUSED_HINT in w for w in result.webapps.warnings)
        )

    def test_repository_is_deleted_when_the_row_cannot_be_saved(self):
        self._static("app")

        with patch.object(GitWebapp, "save", side_effect=IntegrityError("dup")):
            with self.assertRaises(IntegrityError):
                self.run_copy(FakeServers(_static_listing("app")))

        self.git.delete_repository.assert_called_once_with(
            self.target_ws.organization.slug, "target-webapp-app"
        )
