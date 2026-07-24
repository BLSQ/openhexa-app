from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext

from hexa.core.test import GraphQLTestCase
from hexa.data_studio.models import SavedQuery
from hexa.databases.tests.helpers import seed_demo_table

from .testutils import SavedQueryTestMixin


class SavedQuerySchemaTest(SavedQueryTestMixin, GraphQLTestCase):
    def _create_query(
        self,
        user,
        name="My query",
        content="SELECT 1",
        workspace=None,
        description="d",
    ):
        self.client.force_login(user)
        return self.run_query(
            """
            mutation ($input: CreateSavedQueryInput!) {
                createSavedQuery(input: $input) {
                    success
                    errors
                    savedQuery { id name content description createdBy { email } }
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str((workspace or self.WORKSPACE).slug),
                    "name": name,
                    "content": content,
                    "description": description,
                }
            },
        )

    def test_create_saved_query(self):
        r = self._create_query(self.USER_EDITOR)
        payload = r["data"]["createSavedQuery"]
        self.assertTrue(payload["success"])
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["savedQuery"]["name"], "My query")
        self.assertEqual(
            payload["savedQuery"]["createdBy"]["email"], self.USER_EDITOR.email
        )

    def test_create_saved_query_not_member(self):
        r = self._create_query(self.USER_OUTSIDER)
        payload = r["data"]["createSavedQuery"]
        self.assertFalse(payload["success"])
        # Outsider cannot resolve the workspace at all
        self.assertEqual(payload["errors"], ["WORKSPACE_NOT_FOUND"])

    def test_workspace_saved_queries_listing(self):
        self._create_query(self.USER_EDITOR, name="alpha")
        self._create_query(self.USER_ADMIN, name="beta")

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            """
            query ($slug: String!) {
                workspace(slug: $slug) {
                    savedQueries {
                        totalItems
                        items { name permissions { update delete } }
                    }
                }
            }
            """,
            {"slug": str(self.WORKSPACE.slug)},
        )
        result = r["data"]["workspace"]["savedQueries"]
        self.assertEqual(result["totalItems"], 2)
        self.assertCountEqual([i["name"] for i in result["items"]], ["alpha", "beta"])
        # Viewer is not the author of either -> cannot update/delete
        for item in result["items"]:
            self.assertEqual(item["permissions"], {"update": False, "delete": False})

    def test_workspace_saved_queries_isolated_per_workspace(self):
        # USER_ADMIN belongs to both workspaces; each list must only show its own.
        self._create_query(self.USER_ADMIN, name="in-ws1", workspace=self.WORKSPACE)
        self._create_query(self.USER_ADMIN, name="in-ws2", workspace=self.WORKSPACE_2)

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query ($slug: String!) {
                workspace(slug: $slug) { savedQueries { items { name } } }
            }
            """,
            {"slug": str(self.WORKSPACE.slug)},
        )
        items = r["data"]["workspace"]["savedQueries"]["items"]
        self.assertEqual([i["name"] for i in items], ["in-ws1"])

    def test_listing_related_fields_do_not_scale_with_page_size(self):
        """`select_related` must keep related-field loading (createdBy, workspace)
        constant regardless of how many rows the page holds. Guards against a
        regression of the N+1 fix on the data-loading side.
        """
        list_query = """
            query ($slug: String!) {
                workspace(slug: $slug) {
                    savedQueries {
                        items { name createdBy { email } workspace { slug } }
                    }
                }
            }
        """
        variables = {"slug": str(self.WORKSPACE.slug)}

        self._create_query(self.USER_EDITOR, name="q0")
        self.client.force_login(self.USER_VIEWER)
        self.run_query(
            list_query, variables
        )  # warm up one-time caches (session, content types)

        with CaptureQueriesContext(connection) as few:
            self.run_query(list_query, variables)

        for i in range(1, 5):
            self._create_query(self.USER_EDITOR, name=f"q{i}")
        self.client.force_login(self.USER_VIEWER)

        with CaptureQueriesContext(connection) as many:
            self.run_query(list_query, variables)

        self.assertEqual(
            len(many.captured_queries),
            len(few.captured_queries),
            msg="Related-field loading scales with page size — N+1 regression.",
        )

    def test_permissions_true_for_author_and_editor(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        for user in (self.USER_EDITOR, self.USER_ADMIN):
            self.client.force_login(user)
            r = self.run_query(
                "query ($slug: String!, $id: ID!) { savedQuery(workspaceSlug: $slug, id: $id) { permissions { update delete } } }",
                {"slug": str(self.WORKSPACE.slug), "id": query_id},
            )
            self.assertEqual(
                r["data"]["savedQuery"]["permissions"],
                {"update": True, "delete": True},
            )

    def test_saved_queries_search(self):
        self._create_query(self.USER_EDITOR, name="revenue report")
        self._create_query(self.USER_EDITOR, name="patients count")

        def search(term):
            self.client.force_login(self.USER_EDITOR)
            r = self.run_query(
                """
                query ($slug: String!, $query: String) {
                    workspace(slug: $slug) {
                        savedQueries(query: $query) { items { name } }
                    }
                }
                """,
                {"slug": str(self.WORKSPACE.slug), "query": term},
            )
            return [i["name"] for i in r["data"]["workspace"]["savedQueries"]["items"]]

        self.assertEqual(search("revenue"), ["revenue report"])

    def test_saved_queries_search_matches_description_not_content(self):
        self._create_query(
            self.USER_EDITOR, name="alpha", content="SELECT * FROM patients"
        )
        self._create_query(
            self.USER_EDITOR, name="beta", description="quarterly revenue figures"
        )
        self._create_query(self.USER_EDITOR, name="gamma", content="SELECT 1")

        def search(term):
            self.client.force_login(self.USER_EDITOR)
            r = self.run_query(
                """
                query ($slug: String!, $query: String) {
                    workspace(slug: $slug) {
                        savedQueries(query: $query) { items { name } }
                    }
                }
                """,
                {"slug": str(self.WORKSPACE.slug), "query": term},
            )
            return [i["name"] for i in r["data"]["workspace"]["savedQueries"]["items"]]

        self.assertEqual(search("quarterly"), ["beta"])  # matched via description
        # The SQL body is intentionally not searched.
        self.assertEqual(search("patients"), [])

    def test_get_saved_query(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            "query ($slug: String!, $id: ID!) { savedQuery(workspaceSlug: $slug, id: $id) { name } }",
            {"slug": str(self.WORKSPACE.slug), "id": query_id},
        )
        self.assertEqual(r["data"]["savedQuery"]["name"], "My query")

    def test_get_saved_query_outsider(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_OUTSIDER)
        r = self.run_query(
            "query ($slug: String!, $id: ID!) { savedQuery(workspaceSlug: $slug, id: $id) { name } }",
            {"slug": str(self.WORKSPACE.slug), "id": query_id},
        )
        self.assertIsNone(r["data"]["savedQuery"])

    def test_get_saved_query_wrong_workspace(self):
        # A query id that exists but is addressed via a different workspace's
        # slug resolves to nothing: saved queries are scoped to their workspace.
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            "query ($slug: String!, $id: ID!) { savedQuery(workspaceSlug: $slug, id: $id) { name } }",
            {"slug": str(self.WORKSPACE_2.slug), "id": query_id},
        )
        self.assertIsNone(r["data"]["savedQuery"])

    def test_get_saved_query_without_workspace(self):
        # workspaceSlug is optional: omitting it keeps the original id-only
        # lookup (still gated by filter_for_user), so existing callers work.
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            "query ($id: ID!) { savedQuery(id: $id) { name } }",
            {"id": query_id},
        )
        self.assertEqual(r["data"]["savedQuery"]["name"], "My query")

    def test_update_saved_query(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            """
            mutation ($input: UpdateSavedQueryInput!) {
                updateSavedQuery(input: $input) {
                    success errors savedQuery { name content }
                }
            }
            """,
            {"input": {"id": query_id, "name": "Renamed", "content": "SELECT 2"}},
        )
        payload = r["data"]["updateSavedQuery"]
        self.assertTrue(payload["success"])
        self.assertEqual(
            payload["savedQuery"], {"name": "Renamed", "content": "SELECT 2"}
        )

    def test_update_saved_query_partial_and_explicit_null(self):
        created = self._create_query(
            self.USER_EDITOR, name="Original", content="SELECT 1"
        )
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            """
            mutation ($input: UpdateSavedQueryInput!) {
                updateSavedQuery(input: $input) {
                    success errors savedQuery { name content description }
                }
            }
            """,
            # name set; content omitted (must stay); description explicit null (clears to "").
            {"input": {"id": query_id, "name": "Renamed", "description": None}},
        )
        payload = r["data"]["updateSavedQuery"]
        self.assertTrue(payload["success"])
        self.assertEqual(
            payload["savedQuery"],
            {"name": "Renamed", "content": "SELECT 1", "description": ""},
        )

    def test_update_saved_query_not_found(self):
        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            """
            mutation ($input: UpdateSavedQueryInput!) {
                updateSavedQuery(input: $input) { success errors }
            }
            """,
            {"input": {"id": "00000000-0000-0000-0000-000000000000", "name": "x"}},
        )
        payload = r["data"]["updateSavedQuery"]
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["SAVED_QUERY_NOT_FOUND"])

    def test_update_saved_query_denied(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            """
            mutation ($input: UpdateSavedQueryInput!) {
                updateSavedQuery(input: $input) { success errors }
            }
            """,
            {"input": {"id": query_id, "name": "Nope"}},
        )
        payload = r["data"]["updateSavedQuery"]
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["PERMISSION_DENIED"])

    def test_delete_saved_query(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            """
            mutation ($input: DeleteSavedQueryInput!) {
                deleteSavedQuery(input: $input) { success errors }
            }
            """,
            {"input": {"id": query_id}},
        )
        self.assertTrue(r["data"]["deleteSavedQuery"]["success"])
        self.assertFalse(SavedQuery.objects.filter(id=query_id).exists())

    def test_delete_saved_query_not_found(self):
        self.client.force_login(self.USER_OUTSIDER)
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_OUTSIDER)
        r = self.run_query(
            """
            mutation ($input: DeleteSavedQueryInput!) {
                deleteSavedQuery(input: $input) { success errors }
            }
            """,
            {"input": {"id": query_id}},
        )
        payload = r["data"]["deleteSavedQuery"]
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["SAVED_QUERY_NOT_FOUND"])

    def test_get_saved_query_unauthenticated(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.logout()
        r = self.run_query(
            "query ($slug: String!, $id: ID!) { savedQuery(workspaceSlug: $slug, id: $id) { name } }",
            {"slug": str(self.WORKSPACE.slug), "id": query_id},
        )
        self.assertIsNone(r["data"]["savedQuery"])

    def test_create_saved_query_unauthenticated(self):
        self.client.logout()
        r = self.run_query(
            """
            mutation ($input: CreateSavedQueryInput!) {
                createSavedQuery(input: $input) { success }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "name": "n",
                    "content": "SELECT 1",
                }
            },
        )
        # @loginRequired raises before the resolver runs -> null data + top-level error
        self.assertIsNone(r["data"])
        self.assertTrue(r["errors"])


class SavedQueryPublishSchemaTest(SavedQueryTestMixin, GraphQLTestCase):
    def _create(self, user, **overrides):
        self.client.force_login(user)
        variables = {
            "workspaceSlug": str(self.WORKSPACE.slug),
            "name": "My query",
            "content": "SELECT 1",
            **overrides,
        }
        return self.run_query(
            """
            mutation ($input: CreateSavedQueryInput!) {
                createSavedQuery(input: $input) {
                    success
                    errors
                    savedQuery { slug isPublic parameters permissions { run publish } }
                }
            }
            """,
            {"input": variables},
        )

    def test_create_exposes_slug_and_defaults(self):
        payload = self._create(self.USER_EDITOR)["data"]["createSavedQuery"]
        self.assertTrue(payload["success"])
        self.assertEqual(payload["savedQuery"]["slug"], "my-query")
        self.assertFalse(payload["savedQuery"]["isPublic"])
        self.assertEqual(payload["savedQuery"]["parameters"], [])

    def test_create_with_parameters(self):
        payload = self._create(
            self.USER_EDITOR,
            content="SELECT * FROM demo LIMIT {{ limit }}",
            parameters=[{"name": "limit", "type": "integer", "kind": "value"}],
        )["data"]["createSavedQuery"]
        self.assertTrue(payload["success"])
        self.assertEqual(payload["savedQuery"]["parameters"][0]["name"], "limit")

    def test_create_with_invalid_parameters(self):
        payload = self._create(
            self.USER_EDITOR,
            parameters=[{"name": "1bad", "type": "string"}],
        )["data"]["createSavedQuery"]
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["INVALID_PARAMETERS"])

    def test_create_public_denied_for_editor(self):
        payload = self._create(self.USER_EDITOR, isPublic=True)["data"][
            "createSavedQuery"
        ]
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["PERMISSION_DENIED"])

    def test_create_public_allowed_for_admin(self):
        payload = self._create(self.USER_ADMIN, isPublic=True)["data"][
            "createSavedQuery"
        ]
        self.assertTrue(payload["success"])
        self.assertTrue(payload["savedQuery"]["isPublic"])

    def test_permissions_run_and_publish(self):
        payload = self._create(self.USER_EDITOR)["data"]["createSavedQuery"]
        # Editor: can run (any member), cannot publish (admin-only).
        self.assertEqual(
            payload["savedQuery"]["permissions"], {"run": True, "publish": False}
        )

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            "query ($slug: String!) { workspace(slug: $slug) { savedQueries { items { permissions { run publish } } } } }",
            {"slug": str(self.WORKSPACE.slug)},
        )
        admin_view = r["data"]["workspace"]["savedQueries"]["items"][0]["permissions"]
        self.assertEqual(admin_view, {"run": True, "publish": True})


class ExecuteSavedQuerySchemaTest(SavedQueryTestMixin, GraphQLTestCase):
    EXECUTE = """
        mutation ($input: ExecuteSavedQueryInput!) {
            executeSavedQuery(input: $input) {
                success errors errorMessage columns rows rowCount truncated
            }
        }
    """

    def _make(self, content, parameters=None, is_public=False, user=None):
        return SavedQuery.objects.create_if_has_perm(
            user or self.USER_ADMIN,
            self.WORKSPACE,
            name="q",
            content=content,
            parameters=parameters or [],
            is_public=is_public,
        )

    def _execute(self, user, slug, parameters=None):
        self.client.force_login(user)
        return self.run_query(
            self.EXECUTE,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "slug": slug,
                    "parameters": parameters,
                }
            },
        )["data"]["executeSavedQuery"]

    def test_execute_returns_rows(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])
        query = self._make("SELECT id, label FROM demo ORDER BY id")

        payload = self._execute(self.USER_VIEWER, query.slug)

        self.assertTrue(payload["success"])
        self.assertEqual(payload["columns"], ["id", "label"])
        self.assertEqual(
            payload["rows"], [{"id": 1, "label": "a"}, {"id": 2, "label": "b"}]
        )

    def test_execute_binds_parameters(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "a")])
        query = self._make(
            "SELECT id FROM demo WHERE label = {{ label }} ORDER BY id",
            parameters=[{"name": "label", "type": "string", "kind": "value"}],
        )

        payload = self._execute(self.USER_EDITOR, query.slug, {"label": "a"})

        self.assertTrue(payload["success"])
        self.assertEqual(payload["rows"], [{"id": 1}, {"id": 3}])

    def test_execute_injection_payload_is_inert(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])
        query = self._make(
            "SELECT id FROM demo WHERE label = {{ label }}",
            parameters=[{"name": "label", "type": "string", "kind": "value"}],
        )

        payload = self._execute(
            self.USER_EDITOR, query.slug, {"label": "a'; DROP TABLE demo; --"}
        )

        self.assertTrue(payload["success"])
        self.assertEqual(payload["rows"], [])
        # Table survived: the payload was bound, not executed.
        still = self._execute(
            self.USER_EDITOR,
            self._make("SELECT count(*) AS n FROM demo").slug,
        )
        self.assertEqual(still["rows"], [{"n": 2}])

    def test_execute_invalid_parameters(self):
        query = self._make(
            "SELECT * FROM demo LIMIT {{ limit }}",
            parameters=[{"name": "limit", "type": "integer", "kind": "value"}],
        )
        payload = self._execute(self.USER_EDITOR, query.slug, {"limit": "not-a-number"})
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["INVALID_PARAMETERS"])

    def test_execute_unknown_slug(self):
        payload = self._execute(self.USER_EDITOR, "does-not-exist")
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["SAVED_QUERY_NOT_FOUND"])

    def test_execute_outsider_cannot_see_query(self):
        query = self._make("SELECT 1 AS id")
        payload = self._execute(self.USER_OUTSIDER, query.slug)
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["SAVED_QUERY_NOT_FOUND"])


class ExecutePublicSavedQuerySchemaTest(SavedQueryTestMixin, GraphQLTestCase):
    EXECUTE = """
        mutation ($input: ExecuteSavedQueryInput!) {
            executePublicSavedQuery(input: $input) {
                success errors columns rows rowCount truncated
            }
        }
    """

    def setUp(self):
        super().setUp()
        cache.clear()

    def _make(self, content, parameters=None, is_public=True):
        return SavedQuery.objects.create_if_has_perm(
            self.USER_ADMIN,
            self.WORKSPACE,
            name="q",
            content=content,
            parameters=parameters or [],
            is_public=is_public,
        )

    def _execute(self, slug, parameters=None, max_rows=None):
        # Anonymous: no force_login.
        self.client.logout()
        return self.run_query(
            self.EXECUTE,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "slug": slug,
                    "parameters": parameters,
                    "maxRows": max_rows,
                }
            },
        )["data"]["executePublicSavedQuery"]

    def test_anonymous_can_run_public_query(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])
        query = self._make("SELECT id, label FROM demo ORDER BY id")

        payload = self._execute(query.slug)

        self.assertTrue(payload["success"])
        self.assertEqual(
            payload["rows"], [{"id": 1, "label": "a"}, {"id": 2, "label": "b"}]
        )

    def test_anonymous_binds_parameters(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "a")])
        query = self._make(
            "SELECT id FROM demo WHERE label = {{ label }} ORDER BY id",
            parameters=[{"name": "label", "type": "string", "kind": "value"}],
        )

        payload = self._execute(query.slug, {"label": "a"})

        self.assertTrue(payload["success"])
        self.assertEqual(payload["rows"], [{"id": 1}, {"id": 3}])

    def test_non_public_query_is_not_found(self):
        query = self._make("SELECT 1 AS id", is_public=False)
        payload = self._execute(query.slug)
        self.assertFalse(payload["success"])
        # Indistinguishable from a missing query: no existence leak.
        self.assertEqual(payload["errors"], ["SAVED_QUERY_NOT_FOUND"])

    def test_unknown_slug_is_not_found(self):
        payload = self._execute("does-not-exist")
        self.assertFalse(payload["success"])
        self.assertEqual(payload["errors"], ["SAVED_QUERY_NOT_FOUND"])

    def test_public_row_cap_is_enforced(self):
        seed_demo_table(self.WORKSPACE, [(i, "x") for i in range(5)])
        query = self._make("SELECT id FROM demo ORDER BY id")

        with self.settings(PUBLIC_SAVED_QUERY_MAX_ROWS=2):
            payload = self._execute(query.slug)

        self.assertTrue(payload["success"])
        self.assertEqual(payload["rowCount"], 2)
        self.assertTrue(payload["truncated"])

    def test_requested_max_rows_cannot_exceed_public_cap(self):
        seed_demo_table(self.WORKSPACE, [(i, "x") for i in range(5)])
        query = self._make("SELECT id FROM demo ORDER BY id")

        with self.settings(PUBLIC_SAVED_QUERY_MAX_ROWS=2):
            payload = self._execute(query.slug, max_rows=1000)

        self.assertEqual(payload["rowCount"], 2)
        self.assertTrue(payload["truncated"])

    def test_rate_limit(self):
        query = self._make("SELECT 1 AS id")

        with self.settings(PUBLIC_SAVED_QUERY_RATE_LIMIT=1):
            first = self._execute(query.slug)
            second = self._execute(query.slug)

        self.assertTrue(first["success"])
        self.assertFalse(second["success"])
        self.assertEqual(second["errors"], ["RATE_LIMITED"])
