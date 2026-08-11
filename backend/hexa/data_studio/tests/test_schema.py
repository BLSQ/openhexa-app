from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test.utils import CaptureQueriesContext

from hexa.core.test import GraphQLTestCase
from hexa.data_studio.models import QueryLog, SavedQuery
from hexa.databases.tests.helpers import seed_demo_table
from hexa.databases.utils import run_saved_query

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

    def _list(self, order_by=None, page=1, per_page=15):
        self.client.force_login(self.USER_EDITOR)
        variables = {
            "slug": str(self.WORKSPACE.slug),
            "page": page,
            "perPage": per_page,
        }
        # Left out rather than sent as null, so the schema default applies -- which is
        # how a client that does not care about ordering actually calls this.
        if order_by is not None:
            variables["orderBy"] = order_by
        r = self.run_query(
            """
            query ($slug: String!, $orderBy: SavedQueryOrderBy, $page: Int, $perPage: Int) {
                workspace(slug: $slug) {
                    savedQueries(orderBy: $orderBy, page: $page, perPage: $perPage) {
                        items { id name }
                    }
                }
            }
            """,
            variables,
        )
        return r["data"]["workspace"]["savedQueries"]["items"]

    def _list_names(self, order_by=None, page=1, per_page=15):
        return [i["name"] for i in self._list(order_by, page, per_page)]

    def test_saved_queries_default_order_is_most_recently_updated_first(self):
        self._create_query(self.USER_EDITOR, name="alpha")
        self._create_query(self.USER_EDITOR, name="beta")
        SavedQuery.objects.get(name="alpha").save()  # touches updated_at

        self.assertEqual(self._list_names(), ["alpha", "beta"])

    def test_saved_queries_order_by(self):
        self._create_query(self.USER_EDITOR, name="beta")
        self._create_query(self.USER_EDITOR, name="alpha")
        self._create_query(self.USER_EDITOR, name="gamma")

        self.assertEqual(self._list_names("NAME_ASC"), ["alpha", "beta", "gamma"])
        self.assertEqual(self._list_names("NAME_DESC"), ["gamma", "beta", "alpha"])
        # Creation order is also update order, so ascending updated_at replays it.
        self.assertEqual(self._list_names("UPDATED_AT_ASC"), ["beta", "alpha", "gamma"])
        self.assertEqual(
            self._list_names("UPDATED_AT_DESC"), ["gamma", "alpha", "beta"]
        )

    def test_saved_queries_order_by_is_stable_across_pages(self):
        """Rows sharing a sort key must not be dealt to two pages (or none).

        `name` is not unique per workspace, so without a tiebreaker the database
        is free to return duplicates within a page window.
        """
        for _ in range(4):
            self._create_query(self.USER_EDITOR, name="same")

        paged = [
            i["id"]
            for page in (1, 2)
            for i in self._list("NAME_ASC", page=page, per_page=2)
        ]

        self.assertEqual(len(set(paged)), 4)
        self.assertCountEqual(
            paged, [str(pk) for pk in SavedQuery.objects.values_list("id", flat=True)]
        )

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

    BY_SLUG_QUERY = """
        query ($workspaceSlug: String!, $slug: String!) {
            savedQueryBySlug(workspaceSlug: $workspaceSlug, slug: $slug) { id name slug }
        }
    """

    def _get_by_slug(self, user, slug, workspace=None):
        self.client.force_login(user)
        return self.run_query(
            self.BY_SLUG_QUERY,
            {
                "workspaceSlug": str((workspace or self.WORKSPACE).slug),
                "slug": slug,
            },
        )["data"]["savedQueryBySlug"]

    def test_get_saved_query_by_slug(self):
        created = self._create_query(self.USER_EDITOR)["data"]["createSavedQuery"][
            "savedQuery"
        ]

        result = self._get_by_slug(self.USER_VIEWER, "my-query")

        self.assertEqual(
            {"id": created["id"], "name": "My query", "slug": "my-query"}, result
        )

    def test_get_saved_query_by_slug_unknown(self):
        self._create_query(self.USER_EDITOR)
        self.assertIsNone(self._get_by_slug(self.USER_VIEWER, "no-such-query"))

    def test_get_saved_query_by_slug_outsider(self):
        self._create_query(self.USER_EDITOR)
        self.assertIsNone(self._get_by_slug(self.USER_OUTSIDER, "my-query"))

    def test_get_saved_query_by_slug_wrong_workspace(self):
        # Slugs are only unique per workspace, so the pair has to match: the
        # same slug in another workspace must not resolve to this query.
        self._create_query(self.USER_EDITOR, workspace=self.WORKSPACE)

        self.assertIsNone(
            self._get_by_slug(self.USER_ADMIN, "my-query", workspace=self.WORKSPACE_2)
        )

    def test_get_saved_query_by_slug_scoped_to_its_workspace(self):
        self._create_query(self.USER_ADMIN, name="Shared", workspace=self.WORKSPACE)
        other = self._create_query(
            self.USER_ADMIN, name="Shared", workspace=self.WORKSPACE_2
        )["data"]["createSavedQuery"]["savedQuery"]

        result = self._get_by_slug(
            self.USER_ADMIN, "shared", workspace=self.WORKSPACE_2
        )

        self.assertEqual(other["id"], result["id"])

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


class ExecuteSavedQueryTest(SavedQueryTestMixin, GraphQLTestCase):
    """The endpoint web apps use: run a stored query without ever seeing its SQL."""

    EXECUTE_QUERY = """
        query ($input: ExecuteSavedQueryInput!) {
            executeSavedQuery(input: $input) {
                success errors errorMessage columns rows rowCount truncated durationMs
            }
        }
    """

    def _save(self, content, name="Demo", workspace=None, user=None):
        return SavedQuery.objects.create_if_has_perm(
            user or self.USER_EDITOR,
            workspace or self.WORKSPACE,
            name=name,
            content=content,
        )

    def _execute(self, user, slug, workspace=None, max_rows=None):
        self.client.force_login(user)
        payload = {
            "workspaceSlug": str((workspace or self.WORKSPACE).slug),
            "slug": slug,
        }
        if max_rows is not None:
            payload["maxRows"] = max_rows
        return self.run_query(self.EXECUTE_QUERY, {"input": payload})["data"][
            "executeSavedQuery"
        ]

    def test_execute_saved_query(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])
        saved_query = self._save("SELECT id, label FROM demo ORDER BY id")

        result = self._execute(self.USER_VIEWER, saved_query.slug)

        duration_ms = result.pop("durationMs")
        self.assertIsInstance(duration_ms, int)
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "errorMessage": None,
                "columns": ["id", "label"],
                "rows": [{"id": 1, "label": "a"}, {"id": 2, "label": "b"}],
                "rowCount": 2,
                "truncated": False,
            },
            result,
        )

    def test_execute_saved_query_is_audited(self):
        seed_demo_table(self.WORKSPACE, [(1, "a")])
        saved_query = self._save("SELECT id FROM demo")

        self._execute(self.USER_VIEWER, saved_query.slug)

        log = QueryLog.objects.get()
        self.assertEqual(QueryLog.Status.SUCCESS, log.status)
        self.assertEqual(self.USER_VIEWER, log.user)
        # The stored query is named, not just its text: the audit trail has to
        # answer "which saved query ran", which the SQL alone cannot.
        self.assertEqual(saved_query, log.saved_query)
        # No web app in this request, so it is not attributed to one.
        self.assertEqual(QueryLog.Origin.OTHER, log.origin)

    def test_execute_saved_query_unknown_slug(self):
        self._save("SELECT 1")

        result = self._execute(self.USER_VIEWER, "no-such-query")

        self.assertEqual(["NOT_FOUND"], result["errors"])
        self.assertFalse(result["success"])
        # Nothing was executed, so nothing is logged.
        self.assertEqual(0, QueryLog.objects.count())

    def test_execute_saved_query_other_workspace(self):
        saved_query = self._save("SELECT 1")

        result = self._execute(
            self.USER_ADMIN, saved_query.slug, workspace=self.WORKSPACE_2
        )

        self.assertEqual(["NOT_FOUND"], result["errors"])

    def test_execute_saved_query_outsider(self):
        # An outsider cannot see the query at all, so the lookup misses before
        # the run_query permission is ever consulted.
        saved_query = self._save("SELECT 1")

        result = self._execute(self.USER_OUTSIDER, saved_query.slug)

        self.assertEqual(["NOT_FOUND"], result["errors"])

    def test_execute_saved_query_max_rows(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "c")])
        saved_query = self._save("SELECT id FROM demo ORDER BY id")

        result = self._execute(self.USER_VIEWER, saved_query.slug, max_rows=2)

        self.assertEqual(2, result["rowCount"])
        self.assertTrue(result["truncated"])

    def test_execute_saved_query_invalid_sql(self):
        # A query saved against a table that has since been dropped.
        saved_query = self._save("SELECT * FROM gone")

        result = self._execute(self.USER_VIEWER, saved_query.slug)

        self.assertEqual(["QUERY_ERROR"], result["errors"])
        self.assertIn("gone", result["errorMessage"])
        log = QueryLog.objects.get()
        self.assertEqual(QueryLog.Status.ERROR, log.status)
        self.assertEqual(saved_query, log.saved_query)

    def test_execute_saved_query_multiple_statements(self):
        # Nothing stops two statements being saved, so the single-statement rule
        # has to hold at execution time too -- it is what keeps a stored
        # `SET statement_timeout = 0` from running ahead of the query.
        saved_query = self._save("SELECT 1; SELECT 2")

        result = self._execute(self.USER_VIEWER, saved_query.slug)

        self.assertEqual(["MULTIPLE_STATEMENTS"], result["errors"])
        self.assertEqual(QueryLog.Status.REJECTED, QueryLog.objects.get().status)

    def test_run_saved_query_denies_and_logs(self):
        # Not reachable through GraphQL today (seeing a query and being allowed
        # to run one currently coincide), but run_saved_query is a library entry
        # point and owns the check, so the refusal must still be audited.
        saved_query = self._save("SELECT 1")
        request = self.mock_request(self.USER_OUTSIDER)

        with self.assertRaises(PermissionDenied):
            run_saved_query(request, saved_query)

        log = QueryLog.objects.get()
        self.assertEqual(QueryLog.Status.DENIED, log.status)
        self.assertEqual(saved_query, log.saved_query)
