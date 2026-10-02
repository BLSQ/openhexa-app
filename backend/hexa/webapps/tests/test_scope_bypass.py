import json
from unittest.mock import patch

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase, override_settings

from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.datasets.models import Dataset, DatasetLink
from hexa.files.backends.base import ObjectsPage, StorageObject
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import User
from hexa.webapps.middlewares import WEBAPP_SESSION_COOKIE, WEBAPP_SESSION_MAX_AGE
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Connection,
    ConnectionField,
    ConnectionType,
    WorkspaceInvitation,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.testutils import create_workspace

WEBAPPS_DOMAIN = "webapps.test.local"
SECRET_SENTINEL = "SCOPE-BYPASS-SECRET-SENTINEL"
PIPELINE_SENTINEL = "SCOPE-BYPASS-PIPELINE-SENTINEL"
DB_PASSWORD_SENTINEL = "SCOPE-BYPASS-DB-PASSWORD-SENTINEL"
SQL_SENTINEL = "SCOPE_BYPASS_SQL_SENTINEL"
FILE_SENTINEL = "scope-bypass-file-sentinel.csv"
MEMBER_SENTINEL = "scope-bypass-member@test.com"
INVITEE_SENTINEL = "scope-bypass-invitee@test.com"
CONNECTION_NAME_SENTINEL = "SCOPE-BYPASS-CONNECTION-NAME-SENTINEL"
DATASET_SENTINEL = "SCOPE-BYPASS-DATASET-SENTINEL"


class WebappProxyClientMixin:
    def _create_webapp(self, slug, scopes):
        return Webapp.objects.create(
            name=slug,
            slug=slug,
            subdomain=slug,
            url="http://example.com",
            workspace=self.WORKSPACE,
            created_by=self.USER,
            is_public=False,
            allowed_operations=scopes,
        )

    def _post_as_webapp(self, webapp, query):
        session = SessionStore()
        session.set_expiry(WEBAPP_SESSION_MAX_AGE)
        session["user_id"] = str(self.USER.pk)
        session["webapp_id"] = str(webapp.pk)
        session.create()
        self.client.cookies[WEBAPP_SESSION_COOKIE] = session.session_key
        return self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
            HTTP_HOST=f"{webapp.subdomain}.{WEBAPPS_DOMAIN}",
        )


@override_settings(WEBAPPS_DOMAIN=WEBAPPS_DOMAIN, ALLOWED_HOSTS=["*"])
class ScopeBypassTestCase(WebappProxyClientMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        # An admin has every role-based permission, so only the scope check
        # stands between the web app and the data.
        cls.USER = User.objects.create_user("bypass@test.com", "password")
        cls.WORKSPACE = create_workspace(name="Bypass WS")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        connection = Connection.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER,
            name="Secret connection",
            slug="secret-connection",
            connection_type=ConnectionType.CUSTOM,
        )
        ConnectionField.objects.create(
            connection=connection,
            user=cls.USER,
            code="password",
            value=SECRET_SENTINEL,
            secret=True,
        )
        Pipeline.objects.create(
            workspace=cls.WORKSPACE, name=PIPELINE_SENTINEL, code="sentinel"
        )

    def setUp(self):
        self.no_scope_webapp = self._create_webapp("no-scope-app", [])
        self.user_read_webapp = self._create_webapp(
            "user-read-app", [Webapp.OperationScope.USER_READ]
        )


class InlineFragmentBypassTest(ScopeBypassTestCase):
    """A web app must not reach fields outside its scopes by wrapping them in
    an inline fragment on the root type.
    """

    def test_inline_fragment_query_cannot_read_out_of_scope_data(self):
        response = self._post_as_webapp(
            self.no_scope_webapp,
            f"""
            query {{
                ... on Query {{
                    workspace(slug: "{self.WORKSPACE.slug}") {{
                        connections {{ fields {{ code value }} }}
                    }}
                }}
            }}
            """,
        )
        self.assertNotIn(SECRET_SENTINEL, response.content.decode())

    def test_inline_fragment_mutation_cannot_write(self):
        original_name = self.WORKSPACE.name
        self._post_as_webapp(
            self.no_scope_webapp,
            f"""
            mutation {{
                ... on Mutation {{
                    updateWorkspace(input: {{slug: "{self.WORKSPACE.slug}", name: "PWNED"}}) {{
                        success
                    }}
                }}
            }}
            """,
        )
        self.WORKSPACE.refresh_from_db()
        self.assertEqual(self.WORKSPACE.name, original_name)

    def test_inline_fragment_cannot_widen_an_allowed_scope(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            f"""
            query {{
                me {{ user {{ email }} }}
                ... on Query {{
                    pipelines(workspaceSlug: "{self.WORKSPACE.slug}") {{
                        items {{ name }}
                    }}
                }}
            }}
            """,
        )
        self.assertNotIn(PIPELINE_SENTINEL, response.content.decode())

    def test_nested_inline_fragments_are_inspected(self):
        response = self._post_as_webapp(
            self.no_scope_webapp,
            f"""
            query {{
                ... on Query {{
                    ... on Query {{
                        workspace(slug: "{self.WORKSPACE.slug}") {{
                            connections {{ fields {{ code value }} }}
                        }}
                    }}
                }}
            }}
            """,
        )
        self.assertNotIn(SECRET_SENTINEL, response.content.decode())

    def test_root_inline_fragment_is_rejected_even_with_allowed_fields(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            "query { ... on Query { me { user { email } } } }",
        )
        self.assertEqual(response.status_code, 403)


class NamedFragmentBypassTest(ScopeBypassTestCase):
    """A web app must not reach fields outside its scopes by spreading, at the
    root, a fragment named after a field it is allowed to use.
    """

    def test_fragment_named_after_allowed_field_cannot_read_out_of_scope_data(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            f"""
            query {{ ...me }}
            fragment me on Query {{
                pipelines(workspaceSlug: "{self.WORKSPACE.slug}") {{
                    items {{ name }}
                }}
            }}
            """,
        )
        self.assertNotIn(PIPELINE_SENTINEL, response.content.decode())

    def test_fragment_named_after_allowed_field_cannot_write(self):
        original_name = self.WORKSPACE.name
        self._post_as_webapp(
            self.user_read_webapp,
            f"""
            mutation {{ ...me }}
            fragment me on Mutation {{
                updateWorkspace(input: {{slug: "{self.WORKSPACE.slug}", name: "PWNED"}}) {{
                    success
                }}
            }}
            """,
        )
        self.WORKSPACE.refresh_from_db()
        self.assertEqual(self.WORKSPACE.name, original_name)

    def test_fragment_spread_chain_is_inspected(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            f"""
            query {{ ...me }}
            fragment me on Query {{ ...inner }}
            fragment inner on Query {{
                pipelines(workspaceSlug: "{self.WORKSPACE.slug}") {{
                    items {{ name }}
                }}
            }}
            """,
        )
        self.assertNotIn(PIPELINE_SENTINEL, response.content.decode())

    def test_root_fragment_spread_is_rejected_even_with_allowed_fields(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            "query { ...me } fragment me on Query { me { user { email } } }",
        )
        self.assertEqual(response.status_code, 403)


class NestedFieldBypassTest(ScopeBypassTestCase):
    """A scope that grants a root field must not grant everything reachable
    below it: USER_READ covers the current user and their workspace role, and
    nothing else under `workspace`.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.WORKSPACE.db_password = DB_PASSWORD_SENTINEL
        cls.WORKSPACE.bucket_name = "bypass-ws-bucket"
        cls.WORKSPACE.save()
        Connection.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER,
            name=CONNECTION_NAME_SENTINEL,
            slug="named-connection",
            connection_type=ConnectionType.CUSTOM,
        )
        SavedQuery.objects.create(
            workspace=cls.WORKSPACE,
            created_by=cls.USER,
            name="Vetted query",
            content=f"SELECT 1 AS {SQL_SENTINEL}",
            visibility=SavedQueryVisibility.WORKSPACE,
        )
        WorkspaceMembership.objects.create(
            user=User.objects.create_user(MEMBER_SENTINEL, "password"),
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.VIEWER,
        )
        WorkspaceInvitation.objects.create(
            workspace=cls.WORKSPACE,
            email=INVITEE_SENTINEL,
            role=WorkspaceMembershipRole.VIEWER,
            invited_by=cls.USER,
        )
        cls.DATASET = Dataset.objects.create(
            workspace=cls.WORKSPACE,
            created_by=cls.USER,
            name=DATASET_SENTINEL,
            slug="sentinel-dataset",
        )
        DatasetLink.objects.create(
            dataset=cls.DATASET, workspace=cls.WORKSPACE, created_by=cls.USER
        )
        cls.PIPELINE = Pipeline.objects.get(code="sentinel")

    def setUp(self):
        super().setUp()
        self.probe_webapp = self._create_webapp(
            "probe-app",
            [Webapp.OperationScope.USER_READ, Webapp.OperationScope.DATABASE_READ],
        )
        self.pipelines_read_webapp = self._create_webapp(
            "pipelines-read-app", [Webapp.OperationScope.PIPELINES_READ]
        )
        self.datasets_read_webapp = self._create_webapp(
            "datasets-read-app", [Webapp.OperationScope.DATASETS_READ]
        )

    def _query_workspace(self, webapp, selection):
        return self._post_as_webapp(
            webapp,
            f'query {{ workspace(slug: "{self.WORKSPACE.slug}") {{ {selection} }} }}',
        ).content.decode()

    def test_user_read_cannot_read_connection_secrets(self):
        body = self._query_workspace(
            self.probe_webapp, "connections { fields { code value } }"
        )
        self.assertNotIn(SECRET_SENTINEL, body)

    def test_user_read_cannot_list_connections(self):
        body = self._query_workspace(self.probe_webapp, "connections { name }")
        self.assertNotIn(CONNECTION_NAME_SENTINEL, body)

    def test_user_read_cannot_read_database_credentials(self):
        body = self._query_workspace(
            self.probe_webapp, "database { credentials { password } }"
        )
        self.assertNotIn(DB_PASSWORD_SENTINEL, body)

    @patch("hexa.files.schema.types.storage")
    def test_user_read_cannot_list_files(self, mock_storage):
        mock_storage.list_bucket_objects.return_value = ObjectsPage(
            items=[
                StorageObject(
                    key=FILE_SENTINEL,
                    name=FILE_SENTINEL,
                    path=FILE_SENTINEL,
                    size=1,
                    updated_at=None,
                    type="file",
                )
            ],
            has_next_page=False,
            has_previous_page=False,
            page_number=1,
        )
        body = self._query_workspace(
            self.probe_webapp, "bucket { objects { items { name } } }"
        )
        self.assertNotIn(FILE_SENTINEL, body)

    def test_database_read_cannot_read_saved_query_sql(self):
        body = self._query_workspace(
            self.probe_webapp, "savedQueries { items { content } }"
        )
        self.assertNotIn(SQL_SENTINEL, body)

    def test_user_read_cannot_list_other_members(self):
        body = self._query_workspace(
            self.probe_webapp, "members { items { user { email } } }"
        )
        self.assertNotIn(MEMBER_SENTINEL, body)

    def test_user_read_cannot_list_invitations(self):
        body = self._query_workspace(
            self.probe_webapp, "invitations { items { email } }"
        )
        self.assertNotIn(INVITEE_SENTINEL, body)

    def test_user_read_cannot_list_datasets(self):
        body = self._query_workspace(
            self.probe_webapp, "datasets { items { dataset { name } } }"
        )
        self.assertNotIn(DATASET_SENTINEL, body)

    def test_pipeline_root_cannot_reach_workspace_secrets(self):
        body = self._post_as_webapp(
            self.pipelines_read_webapp,
            f"""
            query {{
                pipeline(id: "{self.PIPELINE.id}") {{
                    workspace {{ database {{ credentials {{ password }} }} }}
                }}
            }}
            """,
        ).content.decode()
        self.assertNotIn(DB_PASSWORD_SENTINEL, body)

    def test_dataset_root_cannot_reach_workspace_secrets(self):
        body = self._post_as_webapp(
            self.datasets_read_webapp,
            f"""
            query {{
                dataset(id: "{self.DATASET.id}") {{
                    workspace {{ connections {{ fields {{ code value }} }} }}
                }}
            }}
            """,
        ).content.decode()
        self.assertNotIn(SECRET_SENTINEL, body)


class ScopeAllowedAccessTest(ScopeBypassTestCase):
    """What each scope is meant to grant must keep working once the bypasses
    are closed.
    """

    def test_user_read_returns_current_user(self):
        response = self._post_as_webapp(
            self.user_read_webapp, "query { me { user { email } } }"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)["data"]["me"]["user"]["email"],
            self.USER.email,
        )

    def test_user_read_returns_workspace_identity(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            f'query {{ workspace(slug: "{self.WORKSPACE.slug}") {{ slug name }} }}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)["data"]["workspace"],
            {"slug": self.WORKSPACE.slug, "name": self.WORKSPACE.name},
        )

    def test_pipelines_read_returns_pipeline(self):
        webapp = self._create_webapp(
            "pipelines-read-app", [Webapp.OperationScope.PIPELINES_READ]
        )
        pipeline = Pipeline.objects.get(code="sentinel")
        response = self._post_as_webapp(
            webapp, f'query {{ pipeline(id: "{pipeline.id}") {{ name }} }}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)["data"]["pipeline"]["name"],
            PIPELINE_SENTINEL,
        )


class MainApiFromWebappOriginTest(ScopeBypassTestCase):
    """Web app pages must go through the proxy: their origin must not be able
    to call the main API with the user's session.

    The web app origin is built from the WEBAPPS_DOMAIN the settings were
    loaded with (set by docker-compose for tests and CI), so these tests
    exercise the CORS rules production actually computes from it.
    """

    def setUp(self):
        super().setUp()
        self.assertIsNotNone(
            settings.WEBAPPS_DOMAIN_HOST,
            "WEBAPPS_DOMAIN must be set in the environment for these tests",
        )
        self.webapp_origin = f"https://probe-app.{settings.WEBAPPS_DOMAIN_HOST}"
        self.client.force_login(self.USER)

    def _preflight(self, path, origin):
        return self.client.options(
            path,
            HTTP_ORIGIN=origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

    def test_graphql_preflight_from_webapp_origin_is_refused(self):
        response = self._preflight("/graphql/", self.webapp_origin)
        self.assertNotIn("Access-Control-Allow-Origin", response)

    def test_graphql_post_from_webapp_origin_is_not_readable(self):
        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": "query { me { user { email } } }"}),
            content_type="application/json",
            HTTP_ORIGIN=self.webapp_origin,
        )
        self.assertNotIn("Access-Control-Allow-Origin", response)
        self.assertNotIn("Access-Control-Allow-Credentials", response)

    def test_credentialed_paths_refuse_webapp_origin(self):
        for path in [
            "/mcp/",
            "/oauth/token/",
            "/analytics/track/",
            "/pipelines/runs/some-run/messages/stream/",
            "/assistant/conversations/some-conversation/stream/",
        ]:
            with self.subTest(path=path):
                response = self._preflight(path, self.webapp_origin)
                self.assertNotIn("Access-Control-Allow-Origin", response)

    def test_file_transfer_paths_allow_webapp_origin_without_credentials(self):
        # Download/upload URLs handed out by prepareObjectDownload/Upload point
        # at the main host on the filesystem backend; the token in the URL is
        # the credential, so the session cookie must not come along.
        for path in ["/files/dl/sometoken/", "/files/up/sometoken/"]:
            with self.subTest(path=path):
                response = self._preflight(path, self.webapp_origin)
                self.assertEqual(
                    response.get("Access-Control-Allow-Origin"), self.webapp_origin
                )
                self.assertNotIn("Access-Control-Allow-Credentials", response)

    def test_webapp_origin_cannot_mutate_via_simple_request(self):
        # multipart/form-data is a CORS "simple" request: the browser sends it
        # without a preflight, so CORS alone cannot stop it.
        original_name = self.WORKSPACE.name
        self.client.post(
            "/graphql/",
            data={
                "operations": json.dumps(
                    {
                        "query": f"""
                        mutation {{
                            updateWorkspace(input: {{slug: "{self.WORKSPACE.slug}", name: "PWNED"}}) {{
                                success
                            }}
                        }}
                        """
                    }
                ),
                "map": "{}",
            },
            HTTP_ORIGIN=self.webapp_origin,
        )
        self.WORKSPACE.refresh_from_db()
        self.assertEqual(self.WORKSPACE.name, original_name)

    def test_frontend_origin_keeps_cors_on_graphql(self):
        response = self._preflight("/graphql/", settings.NEW_FRONTEND_DOMAIN)
        self.assertEqual(
            response.get("Access-Control-Allow-Origin"), settings.NEW_FRONTEND_DOMAIN
        )
