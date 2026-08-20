from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test.utils import CaptureQueriesContext

from hexa.core.test import GraphQLTestCase
from hexa.data_studio.models import QueryLog, SavedQuery, SavedQueryVisibility
from hexa.data_studio.query_runner import run_saved_query
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
        visibility="WORKSPACE",
    ):
        """Create a query through the API, workspace-shared unless stated otherwise.

        The mutation defaults to PRIVATE; tests about what one user sees of another
        user's query say which visibility they mean rather than leaning on that
        default.
        """
        self.client.force_login(user)
        return self.run_query(
            """
            mutation ($input: CreateSavedQueryInput!) {
                createSavedQuery(input: $input) {
                    success
                    errors
                    savedQuery {
                        id name content description visibility createdBy { email }
                    }
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str((workspace or self.WORKSPACE).slug),
                    "name": name,
                    "content": content,
                    "description": description,
                    "visibility": visibility,
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

    def test_create_saved_query_defaults_to_private(self):
        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            """
            mutation ($input: CreateSavedQueryInput!) {
                createSavedQuery(input: $input) {
                    success savedQuery { visibility }
                }
            }
            """,
            {
                "input": {
                    "workspaceSlug": str(self.WORKSPACE.slug),
                    "name": "Draft",
                    "content": "SELECT 1",
                }
            },
        )
        payload = r["data"]["createSavedQuery"]
        self.assertTrue(payload["success"])
        self.assertEqual("PRIVATE", payload["savedQuery"]["visibility"])

    def test_create_saved_query_shared(self):
        r = self._create_query(self.USER_EDITOR, visibility="WORKSPACE")
        self.assertEqual(
            "WORKSPACE", r["data"]["createSavedQuery"]["savedQuery"]["visibility"]
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

    def test_workspace_saved_queries_listing_excludes_others_private(self):
        self._create_query(self.USER_EDITOR, name="shared")
        self._create_query(self.USER_EDITOR, name="editor-draft", visibility="PRIVATE")
        self._create_query(self.USER_VIEWER, name="viewer-draft", visibility="PRIVATE")

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            """
            query ($slug: String!) {
                workspace(slug: $slug) {
                    savedQueries { totalItems items { name visibility } }
                }
            }
            """,
            {"slug": str(self.WORKSPACE.slug)},
        )
        result = r["data"]["workspace"]["savedQueries"]
        # The viewer's own draft counts, the editor's does not - including in the
        # total, or paging would advertise rows that are never returned.
        self.assertEqual(2, result["totalItems"])
        self.assertCountEqual(
            ["shared", "viewer-draft"], [i["name"] for i in result["items"]]
        )

    def test_get_other_members_private_query_is_not_found(self):
        created = self._create_query(self.USER_EDITOR, visibility="PRIVATE")
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            "query ($id: ID!) { savedQuery(id: $id) { name } }",
            {"id": query_id},
        )
        self.assertIsNone(r["data"]["savedQuery"])

    def test_update_saved_query_visibility(self):
        created = self._create_query(self.USER_EDITOR, visibility="PRIVATE")
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(
            """
            mutation ($input: UpdateSavedQueryInput!) {
                updateSavedQuery(input: $input) {
                    success errors savedQuery { visibility }
                }
            }
            """,
            {"input": {"id": query_id, "visibility": "WORKSPACE"}},
        )
        payload = r["data"]["updateSavedQuery"]
        self.assertTrue(payload["success"])
        self.assertEqual("WORKSPACE", payload["savedQuery"]["visibility"])

    def test_update_saved_query_visibility_denied_for_non_author(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            mutation ($input: UpdateSavedQueryInput!) {
                updateSavedQuery(input: $input) { success errors }
            }
            """,
            {"input": {"id": query_id, "visibility": "PRIVATE"}},
        )
        payload = r["data"]["updateSavedQuery"]
        self.assertFalse(payload["success"])
        self.assertEqual(["PERMISSION_DENIED"], payload["errors"])
        self.assertEqual("WORKSPACE", SavedQuery.objects.get(id=query_id).visibility)

    def test_saved_query_permissions_update_visibility(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        permissions_query = """
            query ($id: ID!) {
                savedQuery(id: $id) {
                    permissions { update delete updateVisibility }
                }
            }
        """
        variables = {"id": query_id}

        self.client.force_login(self.USER_EDITOR)
        r = self.run_query(permissions_query, variables)
        self.assertEqual(
            {"update": True, "delete": True, "updateVisibility": True},
            r["data"]["savedQuery"]["permissions"],
        )

        # The admin may edit and delete a shared query, but not unshare it.
        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(permissions_query, variables)
        self.assertEqual(
            {"update": True, "delete": True, "updateVisibility": False},
            r["data"]["savedQuery"]["permissions"],
        )

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
                "query ($id: ID!) { savedQuery(id: $id) { permissions { update delete } } }",
                {"id": query_id},
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
            "query ($id: ID!) { savedQuery(id: $id) { name } }",
            {"id": query_id},
        )
        self.assertEqual(r["data"]["savedQuery"]["name"], "My query")

    def test_get_saved_query_outsider(self):
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_OUTSIDER)
        r = self.run_query(
            "query ($id: ID!) { savedQuery(id: $id) { name } }",
            {"id": query_id},
        )
        self.assertIsNone(r["data"]["savedQuery"])

    def test_get_saved_query_from_other_workspace(self):
        # The id alone carries no authority: a member of WORKSPACE cannot read a
        # query living in WORKSPACE_2, which is what makes the workspace safe to
        # leave out of the field's arguments.
        created = self._create_query(self.USER_ADMIN, workspace=self.WORKSPACE_2)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            "query ($id: ID!) { savedQuery(id: $id) { name } }",
            {"id": query_id},
        )
        self.assertIsNone(r["data"]["savedQuery"])

    def test_get_saved_query_exposes_its_workspace(self):
        # Callers that render a query under a workspace-scoped URL need the
        # owning workspace to detect a mismatch themselves.
        created = self._create_query(self.USER_EDITOR)
        query_id = created["data"]["createSavedQuery"]["savedQuery"]["id"]

        self.client.force_login(self.USER_VIEWER)
        r = self.run_query(
            "query ($id: ID!) { savedQuery(id: $id) { workspace { slug } } }",
            {"id": query_id},
        )
        self.assertEqual(
            r["data"]["savedQuery"]["workspace"]["slug"], self.WORKSPACE.slug
        )

    BY_SLUG_QUERY = """
        query ($slug: String!) {
            savedQueryBySlug(slug: $slug) { id name slug }
        }
    """

    def _get_by_slug(self, user, slug):
        self.client.force_login(user)
        return self.run_query(self.BY_SLUG_QUERY, {"slug": slug})["data"][
            "savedQueryBySlug"
        ]

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

    def test_get_saved_query_by_slug_resolves_one_query_across_workspaces(self):
        # Slugs are unique across workspaces, so the same name in a second
        # workspace is suffixed and each slug still resolves to its own query.
        first = self.create_saved_query(
            user=self.USER_ADMIN, workspace=self.WORKSPACE, name="Shared"
        )
        second = self.create_saved_query(
            user=self.USER_ADMIN, workspace=self.WORKSPACE_2, name="Shared"
        )

        self.assertNotEqual(first.slug, second.slug)
        self.assertEqual(
            str(first.id), self._get_by_slug(self.USER_ADMIN, first.slug)["id"]
        )
        self.assertEqual(
            str(second.id), self._get_by_slug(self.USER_ADMIN, second.slug)["id"]
        )

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
            "query ($id: ID!) { savedQuery(id: $id) { name } }",
            {"id": query_id},
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

    def _execute(self, user, slug, max_rows=None):
        self.client.force_login(user)
        payload = {"slug": slug}
        if max_rows is not None:
            payload["maxRows"] = max_rows
        return self.run_query(self.EXECUTE_QUERY, {"input": payload})["data"][
            "executeSavedQuery"
        ]

    def test_execute_saved_query(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b")])
        saved_query = self.create_saved_query(
            content="SELECT id, label FROM demo ORDER BY id"
        )

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
        saved_query = self.create_saved_query(content="SELECT id FROM demo")

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
        self.create_saved_query(content="SELECT 1")

        result = self._execute(self.USER_VIEWER, "no-such-query")

        self.assertEqual(["SAVED_QUERY_NOT_FOUND"], result["errors"])
        self.assertFalse(result["success"])
        # Nothing was executed, so nothing is logged.
        self.assertEqual(0, QueryLog.objects.count())

    def test_execute_saved_query_of_a_workspace_the_caller_is_not_in(self):
        # The input names no workspace, so visibility is what scopes the lookup:
        # a query in a workspace the caller does not belong to stays unreachable.
        saved_query = self.create_saved_query(
            user=self.USER_ADMIN,
            workspace=self.WORKSPACE_2,
            content="SELECT 1",
            visibility=SavedQueryVisibility.WORKSPACE,
        )

        result = self._execute(self.USER_VIEWER, saved_query.slug)

        self.assertEqual(["SAVED_QUERY_NOT_FOUND"], result["errors"])

    def test_execute_saved_query_outsider(self):
        # An outsider cannot see the query at all, so the lookup misses before
        # the run_query permission is ever consulted.
        saved_query = self.create_saved_query(content="SELECT 1")

        result = self._execute(self.USER_OUTSIDER, saved_query.slug)

        self.assertEqual(["SAVED_QUERY_NOT_FOUND"], result["errors"])

    def test_execute_saved_query_max_rows(self):
        seed_demo_table(self.WORKSPACE, [(1, "a"), (2, "b"), (3, "c")])
        saved_query = self.create_saved_query(content="SELECT id FROM demo ORDER BY id")

        result = self._execute(self.USER_VIEWER, saved_query.slug, max_rows=2)

        self.assertEqual(2, result["rowCount"])
        self.assertTrue(result["truncated"])

    def test_execute_saved_query_invalid_sql(self):
        # A query saved against a table that has since been dropped.
        saved_query = self.create_saved_query(content="SELECT * FROM gone")

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
        saved_query = self.create_saved_query(content="SELECT 1; SELECT 2")

        result = self._execute(self.USER_VIEWER, saved_query.slug)

        self.assertEqual(["MULTIPLE_STATEMENTS"], result["errors"])
        self.assertEqual(QueryLog.Status.REJECTED, QueryLog.objects.get().status)

    def test_run_saved_query_denies_and_logs(self):
        # Not reachable through GraphQL today (seeing a query and being allowed
        # to run one currently coincide), but run_saved_query is a library entry
        # point and owns the check, so the refusal must still be audited.
        saved_query = self.create_saved_query(content="SELECT 1")
        request = self.mock_request(self.USER_OUTSIDER)

        with self.assertRaises(PermissionDenied):
            run_saved_query(request, saved_query)

        log = QueryLog.objects.get()
        self.assertEqual(QueryLog.Status.DENIED, log.status)
        self.assertEqual(saved_query, log.saved_query)
