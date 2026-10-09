import json
from unittest.mock import patch

from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase, override_settings

from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.datasets.models import Dataset, DatasetLink
from hexa.files.backends.base import ObjectsPage, StorageObject
from hexa.pipelines.models import Pipeline, PipelineRun
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

    def _assert_refused(self, response, field):
        self.assertEqual(response.status_code, 403)
        self.assertIn(field, json.loads(response.content)["errors"][0]["message"])

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
        self._assert_refused(response, "Query.workspace")
        self.assertNotIn(SECRET_SENTINEL, response.content.decode())

    def test_inline_fragment_mutation_cannot_write(self):
        original_name = self.WORKSPACE.name
        response = self._post_as_webapp(
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
        self._assert_refused(response, "Mutation.updateWorkspace")
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
        self._assert_refused(response, "Query.pipelines")
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
        self._assert_refused(response, "Query.workspace")
        self.assertNotIn(SECRET_SENTINEL, response.content.decode())

    def test_root_inline_fragment_with_allowed_fields_is_accepted(self):
        for query in [
            "query { ... on Query { me { user { email } } } }",
            "query ($withUser: Boolean = true) "
            "{ ... @include(if: $withUser) { me { user { email } } } }",
        ]:
            with self.subTest(query=query):
                response = self._post_as_webapp(self.user_read_webapp, query)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    json.loads(response.content)["data"]["me"]["user"]["email"],
                    self.USER.email,
                )


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
        self._assert_refused(response, "Query.pipelines")
        self.assertNotIn(PIPELINE_SENTINEL, response.content.decode())

    def test_fragment_named_after_allowed_field_cannot_write(self):
        original_name = self.WORKSPACE.name
        response = self._post_as_webapp(
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
        self._assert_refused(response, "Mutation.updateWorkspace")
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
        self._assert_refused(response, "Query.pipelines")
        self.assertNotIn(PIPELINE_SENTINEL, response.content.decode())

    def test_root_fragment_spread_with_allowed_fields_is_accepted(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            "query { ...me } fragment me on Query { me { user { email } } }",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)["data"]["me"]["user"]["email"],
            self.USER.email,
        )


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
        )

    def test_user_read_cannot_read_connection_secrets(self):
        response = self._query_workspace(
            self.probe_webapp, "connections { fields { code value } }"
        )
        self._assert_refused(response, "Workspace.connections")
        self.assertNotIn(SECRET_SENTINEL, response.content.decode())

    def test_user_read_cannot_list_connections(self):
        response = self._query_workspace(self.probe_webapp, "connections { name }")
        self._assert_refused(response, "Workspace.connections")
        self.assertNotIn(CONNECTION_NAME_SENTINEL, response.content.decode())

    def test_user_read_cannot_read_database_credentials(self):
        response = self._query_workspace(
            self.probe_webapp, "database { credentials { password } }"
        )
        self._assert_refused(response, "Workspace.database")
        self.assertNotIn(DB_PASSWORD_SENTINEL, response.content.decode())

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
        response = self._query_workspace(
            self.probe_webapp, "bucket { objects { items { name } } }"
        )
        self._assert_refused(response, "Workspace.bucket")
        self.assertNotIn(FILE_SENTINEL, response.content.decode())

    def test_database_read_cannot_read_saved_query_sql(self):
        response = self._query_workspace(
            self.probe_webapp, "savedQueries { items { content } }"
        )
        self._assert_refused(response, "Workspace.savedQueries")
        self.assertNotIn(SQL_SENTINEL, response.content.decode())

    def test_user_read_cannot_list_other_members(self):
        response = self._query_workspace(
            self.probe_webapp, "members { items { user { email } } }"
        )
        self._assert_refused(response, "Workspace.members")
        self.assertNotIn(MEMBER_SENTINEL, response.content.decode())

    def test_user_read_cannot_list_invitations(self):
        response = self._query_workspace(
            self.probe_webapp, "invitations { items { email } }"
        )
        self._assert_refused(response, "Workspace.invitations")
        self.assertNotIn(INVITEE_SENTINEL, response.content.decode())

    def test_user_read_cannot_list_datasets(self):
        response = self._query_workspace(
            self.probe_webapp, "datasets { items { dataset { name } } }"
        )
        self._assert_refused(response, "Workspace.datasets")
        self.assertNotIn(DATASET_SENTINEL, response.content.decode())

    def test_pipeline_root_cannot_reach_workspace_secrets(self):
        response = self._post_as_webapp(
            self.pipelines_read_webapp,
            f"""
            query {{
                pipeline(id: "{self.PIPELINE.id}") {{
                    workspace {{ database {{ credentials {{ password }} }} }}
                }}
            }}
            """,
        )
        self._assert_refused(response, "Pipeline.workspace")
        self.assertNotIn(DB_PASSWORD_SENTINEL, response.content.decode())

    def test_dataset_root_cannot_reach_workspace_secrets(self):
        response = self._post_as_webapp(
            self.datasets_read_webapp,
            f"""
            query {{
                dataset(id: "{self.DATASET.id}") {{
                    workspace {{ connections {{ fields {{ code value }} }} }}
                }}
            }}
            """,
        )
        self._assert_refused(response, "Workspace.connections")
        self.assertNotIn(SECRET_SENTINEL, response.content.decode())


class MutationResultBypassTest(ScopeBypassTestCase):
    """A mutation's result must not be a way back into the workspace."""

    def test_run_pipeline_result_cannot_reach_workspace_secrets(self):
        webapp = self._create_webapp("run-app", [Webapp.OperationScope.PIPELINES_RUN])
        pipeline = Pipeline.objects.get(code="sentinel")
        response = self._post_as_webapp(
            webapp,
            f"""
            mutation {{
                runPipeline(input: {{id: "{pipeline.id}", config: {{}}}}) {{
                    run {{ pipeline {{ workspace {{ database {{ credentials {{ password }} }} }} }} }}
                }}
            }}
            """,
        )
        self._assert_refused(response, "PipelineRun.pipeline")
        self.assertFalse(PipelineRun.objects.filter(pipeline=pipeline).exists())

    def test_create_dataset_result_cannot_reach_workspace_secrets(self):
        webapp = self._create_webapp(
            "dataset-write-app", [Webapp.OperationScope.DATASETS_WRITE]
        )
        response = self._post_as_webapp(
            webapp,
            f"""
            mutation {{
                createDataset(input: {{workspaceSlug: "{self.WORKSPACE.slug}", name: "Probe"}}) {{
                    dataset {{ workspace {{ connections {{ fields {{ code value }} }} }} }}
                }}
            }}
            """,
        )
        self._assert_refused(response, "Dataset.workspace")
        self.assertFalse(Dataset.objects.filter(name="Probe").exists())


class StaticCheckTest(ScopeBypassTestCase):
    def test_skipped_field_is_still_refused(self):
        """The check reads the query, not what ends up executing: a field the
        query skips is refused all the same.
        """
        response = self._post_as_webapp(
            self.user_read_webapp,
            f"""
            query {{
                workspace(slug: "{self.WORKSPACE.slug}") {{
                    slug
                    connections @include(if: false) {{ name }}
                }}
            }}
            """,
        )
        self._assert_refused(response, "Workspace.connections")


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

    def test_user_read_returns_viewer_role(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            f'query {{ workspace(slug: "{self.WORKSPACE.slug}") {{ currentMembership {{ role }} }} }}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)["data"]["workspace"]["currentMembership"],
            {"role": "ADMIN"},
        )

    def test_user_read_role_does_not_open_the_membership(self):
        response = self._post_as_webapp(
            self.user_read_webapp,
            f'query {{ workspace(slug: "{self.WORKSPACE.slug}") '
            "{ currentMembership { workspace { connections { name } } } } }",
        )
        self._assert_refused(response, "WorkspaceMembership.workspace")

    def test_pipeline_permissions_reflect_the_web_app_scopes(self):
        """The viewer is an admin, but only a web app with PIPELINES_RUN can run."""
        pipeline = Pipeline.objects.get(code="sentinel")
        query = f'query {{ pipeline(id: "{pipeline.id}") {{ permissions {{ run }} }} }}'
        for slug, scopes, can_run in [
            ("read-only-app", [Webapp.OperationScope.PIPELINES_READ], False),
            (
                "read-run-app",
                [
                    Webapp.OperationScope.PIPELINES_READ,
                    Webapp.OperationScope.PIPELINES_RUN,
                ],
                True,
            ),
        ]:
            with self.subTest(scopes=scopes):
                response = self._post_as_webapp(
                    self._create_webapp(slug, scopes), query
                )
                self.assertEqual(
                    json.loads(response.content)["data"]["pipeline"]["permissions"],
                    {"run": can_run},
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
