import json
from unittest.mock import patch

from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase, override_settings

from hexa.core.test import GraphQLTestCase
from hexa.datasets.models import Dataset, DatasetLink
from hexa.files.backends.base import StorageObject
from hexa.pipelines.models import Pipeline, PipelineRun, PipelineVersion
from hexa.user_management.models import User
from hexa.webapps.graphql_proxy import extract_top_level_fields
from hexa.webapps.middlewares import WEBAPP_SESSION_COOKIE, WEBAPP_SESSION_MAX_AGE
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

WEBAPPS_DOMAIN = "webapps.test.local"


class ExtractTopLevelFieldsTest(TestCase):
    def test_simple_query(self):
        query = 'query { pipeline(id: "abc") { id name } }'
        self.assertEqual(extract_top_level_fields(query), {"pipeline"})

    def test_simple_mutation(self):
        query = 'mutation { runPipeline(input: {id: "abc"}) { success } }'
        self.assertEqual(extract_top_level_fields(query), {"runPipeline"})

    def test_multiple_fields(self):
        query = 'query { pipeline(id: "abc") { id } me { email } }'
        self.assertEqual(extract_top_level_fields(query), {"pipeline", "me"})

    def test_named_operation(self):
        query = 'query GetPipeline { pipeline(id: "abc") { id name } }'
        self.assertEqual(extract_top_level_fields(query), {"pipeline"})

    def test_multiple_operations(self):
        query = """
            query A { pipeline(id: "a") { id } }
            query B { me { email } workspace(slug: "w") { name } }
        """
        self.assertEqual(
            extract_top_level_fields(query), {"pipeline", "me", "workspace"}
        )

    def test_with_fragments(self):
        query = """
            query { pipeline(id: "abc") { ...PipelineFields } }
            fragment PipelineFields on Pipeline { id name }
        """
        self.assertEqual(extract_top_level_fields(query), {"pipeline"})

    def test_aliased_field(self):
        query = 'query { myPipeline: pipeline(id: "abc") { id } }'
        self.assertEqual(extract_top_level_fields(query), {"pipeline"})

    def test_introspection_field(self):
        query = "query { __typename }"
        self.assertEqual(extract_top_level_fields(query), {"__typename"})

    def test_invalid_query_raises(self):
        with self.assertRaises(Exception):
            extract_top_level_fields("not a query {{{")


@override_settings(
    WEBAPPS_DOMAIN=WEBAPPS_DOMAIN,
    ALLOWED_HOSTS=["*"],
)
class GraphQLProxyMiddlewareTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("proxy@test.com", "password")
        cls.WORKSPACE = Workspace.objects.create(name="Proxy WS")
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WEBAPP_PRIVATE = Webapp.objects.create(
            name="Private App",
            slug="private-app",
            subdomain="private-app",
            url="http://example.com",
            workspace=cls.WORKSPACE,
            created_by=cls.USER,
            is_public=False,
            allowed_operations=[
                Webapp.OperationScope.PIPELINES_READ,
                Webapp.OperationScope.USER_READ,
            ],
        )
        cls.WEBAPP_PUBLIC = Webapp.objects.create(
            name="Public App",
            slug="public-app",
            subdomain="public-app",
            url="http://example.com",
            workspace=cls.WORKSPACE,
            created_by=cls.USER,
            is_public=True,
        )

    def _create_webapp_session(self, webapp, user):
        session = SessionStore()
        session.set_expiry(WEBAPP_SESSION_MAX_AGE)
        session["user_id"] = str(user.pk)
        session["webapp_id"] = str(webapp.pk)
        session.create()
        return session

    def _graphql_post(self, subdomain, query, session_key=None, extra_headers=None):
        kwargs = {
            "data": json.dumps({"query": query}),
            "content_type": "application/json",
            "HTTP_HOST": f"{subdomain}.{WEBAPPS_DOMAIN}",
            **(extra_headers or {}),
        }
        if session_key:
            self.client.cookies[WEBAPP_SESSION_COOKIE] = session_key
        return self.client.post("/graphql/", **kwargs)

    def test_public_webapp_graphql_returns_404(self):
        response = self._graphql_post("public-app", "query { me { user { email } } }")
        self.assertEqual(response.status_code, 404)

    def test_no_session_returns_401(self):
        response = self._graphql_post("private-app", "query { me { user { email } } }")
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertEqual(data["errors"][0]["message"], "Authentication required")

    def test_allowed_pipeline_query_returns_data(self):
        pipeline = Pipeline.objects.create(
            workspace=self.WORKSPACE,
            name="Test Pipeline",
            code="test-pipeline",
        )
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            f'query {{ pipeline(id: "{pipeline.id}") {{ id name }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["pipeline"]["id"], str(pipeline.id))
        self.assertEqual(data["data"]["pipeline"]["name"], "Test Pipeline")

    def _create_scoped_webapp(self, slug, scopes):
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

    def test_allowed_workspace_query_returns_data(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            f'query {{ workspace(slug: "{self.WORKSPACE.slug}") {{ slug name }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["workspace"]["slug"], self.WORKSPACE.slug)
        self.assertEqual(data["data"]["workspace"]["name"], self.WORKSPACE.name)

    def test_allowed_pipelines_list_query_returns_data(self):
        Pipeline.objects.create(workspace=self.WORKSPACE, name="Alpha", code="alpha")
        Pipeline.objects.create(workspace=self.WORKSPACE, name="Beta", code="beta")
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            f'query {{ pipelines(workspaceSlug: "{self.WORKSPACE.slug}") {{ items {{ code name }} }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        codes = {p["code"] for p in data["data"]["pipelines"]["items"]}
        self.assertEqual(codes, {"alpha", "beta"})

    def test_allowed_pipeline_by_code_query_returns_data(self):
        Pipeline.objects.create(
            workspace=self.WORKSPACE, name="By Code", code="by-code"
        )
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            f'query {{ pipelineByCode(workspaceSlug: "{self.WORKSPACE.slug}", code: "by-code") {{ code name }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["pipelineByCode"]["code"], "by-code")
        self.assertEqual(data["data"]["pipelineByCode"]["name"], "By Code")

    def test_allowed_run_pipeline_mutation_creates_run(self):
        pipeline = Pipeline.objects.create(
            workspace=self.WORKSPACE, name="Runnable", code="runnable"
        )
        PipelineVersion.objects.create(
            pipeline=pipeline,
            version_number=1,
            description="v1",
            zipfile=b"some_bytes",
        )
        webapp = self._create_scoped_webapp(
            "run-app", [Webapp.OperationScope.PIPELINES_RUN]
        )
        session = self._create_webapp_session(webapp, self.USER)
        response = self._graphql_post(
            "run-app",
            f'mutation {{ runPipeline(input: {{id: "{pipeline.id}", config: {{}}}}) {{ success errors run {{ id }} }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["data"]["runPipeline"]["success"])
        self.assertEqual(data["data"]["runPipeline"]["errors"], [])
        run = PipelineRun.objects.get(id=data["data"]["runPipeline"]["run"]["id"])
        self.assertEqual(run.pipeline, pipeline)
        self.assertEqual(run.user, self.USER)

    @patch("hexa.files.schema.queries.storage")
    def test_allowed_get_file_by_path_query_returns_file(self, mock_storage):
        self.WORKSPACE.bucket_name = "proxy-ws-bucket"
        self.WORKSPACE.save()
        mock_storage.get_bucket_object.return_value = StorageObject(
            key="data.csv",
            name="data.csv",
            path="folder/data.csv",
            size=42,
            updated_at=None,
            type="file",
        )
        webapp = self._create_scoped_webapp(
            "files-read-app", [Webapp.OperationScope.FILES_READ]
        )
        session = self._create_webapp_session(webapp, self.USER)
        response = self._graphql_post(
            "files-read-app",
            f'query {{ getFileByPath(workspaceSlug: "{self.WORKSPACE.slug}", path: "folder/data.csv") {{ name path size }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(
            data["data"]["getFileByPath"],
            {"name": "data.csv", "path": "folder/data.csv", "size": 42},
        )
        mock_storage.get_bucket_object.assert_called_once_with(
            "proxy-ws-bucket", "folder/data.csv"
        )

    @patch("hexa.files.schema.mutations.storage")
    def test_allowed_prepare_object_upload_mutation_returns_upload_url(
        self, mock_storage
    ):
        self.WORKSPACE.bucket_name = "proxy-ws-bucket"
        self.WORKSPACE.save()
        mock_storage.generate_upload_url.return_value = (
            "https://signed.example.com/upload",
            {"X-Upload-Header": "yes"},
        )
        webapp = self._create_scoped_webapp(
            "files-write-app", [Webapp.OperationScope.FILES_WRITE]
        )
        session = self._create_webapp_session(webapp, self.USER)
        response = self._graphql_post(
            "files-write-app",
            f'mutation {{ prepareObjectUpload(input: {{workspaceSlug: "{self.WORKSPACE.slug}", objectKey: "uploads/file.bin"}}) {{ success errors uploadUrl }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["data"]["prepareObjectUpload"]["success"])
        self.assertEqual(data["data"]["prepareObjectUpload"]["errors"], [])
        self.assertEqual(
            data["data"]["prepareObjectUpload"]["uploadUrl"],
            "https://signed.example.com/upload",
        )
        mock_storage.generate_upload_url.assert_called_once()
        call_kwargs = mock_storage.generate_upload_url.call_args.kwargs
        self.assertEqual(call_kwargs["bucket_name"], "proxy-ws-bucket")
        self.assertEqual(call_kwargs["target_key"], "uploads/file.bin")

    def test_allowed_dataset_query_returns_data(self):
        dataset = Dataset.objects.create(
            workspace=self.WORKSPACE,
            created_by=self.USER,
            name="Webapp Read",
            slug="webapp-read",
        )
        DatasetLink.objects.create(
            dataset=dataset, workspace=self.WORKSPACE, created_by=self.USER
        )
        webapp = self._create_scoped_webapp(
            "datasets-read-app", [Webapp.OperationScope.DATASETS_READ]
        )
        session = self._create_webapp_session(webapp, self.USER)
        response = self._graphql_post(
            "datasets-read-app",
            f'query {{ dataset(id: "{dataset.id}") {{ id name slug }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["dataset"]["id"], str(dataset.id))
        self.assertEqual(data["data"]["dataset"]["name"], "Webapp Read")

    def test_allowed_create_dataset_mutation_returns_data(self):
        webapp = self._create_scoped_webapp(
            "datasets-write-app", [Webapp.OperationScope.DATASETS_WRITE]
        )
        session = self._create_webapp_session(webapp, self.USER)
        response = self._graphql_post(
            "datasets-write-app",
            f'mutation {{ createDataset(input: {{workspaceSlug: "{self.WORKSPACE.slug}", name: "Webapp Dataset", description: "From webapp"}}) {{ success errors dataset {{ name slug }} }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["data"]["createDataset"]["success"])
        self.assertEqual(data["data"]["createDataset"]["errors"], [])
        self.assertEqual(
            data["data"]["createDataset"]["dataset"]["name"], "Webapp Dataset"
        )
        dataset = Dataset.objects.get(
            workspace=self.WORKSPACE,
            slug=data["data"]["createDataset"]["dataset"]["slug"],
        )
        self.assertEqual(dataset.name, "Webapp Dataset")
        self.assertEqual(dataset.created_by, self.USER)

    def test_allowed_me_query_returns_authenticated_user(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            "query { me { user { email } } }",
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["data"]["me"]["user"]["email"], self.USER.email)

    def test_disallowed_operation_returns_403(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            "mutation { runPipeline(input: {}) { success } }",
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertIn("runPipeline", data["errors"][0]["message"])

    def test_introspection_passes_through(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            "query { __typename }",
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)

    def test_mixed_allowed_and_disallowed_returns_403(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            'query { pipeline(id: "00000000-0000-0000-0000-000000000000") { id } getFileByPath(objectKey: "f", workspaceSlug: "w") { name } }',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_json_returns_400(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        self.client.cookies[WEBAPP_SESSION_COOKIE] = session.session_key
        response = self.client.post(
            "/graphql/",
            data="not json",
            content_type="application/json",
            HTTP_HOST=f"private-app.{WEBAPPS_DOMAIN}",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data["errors"][0]["message"], "Invalid request body")

    def test_get_request_returns_405(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        self.client.cookies[WEBAPP_SESSION_COOKIE] = session.session_key
        response = self.client.get(
            "/graphql/",
            HTTP_HOST=f"private-app.{WEBAPPS_DOMAIN}",
        )
        self.assertEqual(response.status_code, 405)

    def test_cross_origin_request_returns_403(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            "query { me { user { email } } }",
            session_key=session.session_key,
            extra_headers={"HTTP_ORIGIN": "https://evil.example.com"},
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data["errors"][0]["message"], "Origin not allowed")

    def test_same_origin_request_succeeds(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            "query { me { user { email } } }",
            session_key=session.session_key,
            extra_headers={"HTTP_ORIGIN": f"http://private-app.{WEBAPPS_DOMAIN}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_preview_session_key_host_origin_succeeds(self):
        # Preview URLs serve the webapp from a session-key subdomain rather
        # than the webapp's own subdomain — same-origin queries must still pass.
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        preview_host = f"{session.session_key}.{WEBAPPS_DOMAIN}"
        self.client.cookies[WEBAPP_SESSION_COOKIE] = session.session_key
        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": "query { me { user { email } } }"}),
            content_type="application/json",
            HTTP_HOST=preview_host,
            HTTP_ORIGIN=f"http://{preview_host}",
        )
        self.assertEqual(response.status_code, 200)

    def test_custom_domain_host_origin_succeeds(self):
        self.WEBAPP_PRIVATE.custom_domain = "my-custom-domain.example.com"
        self.WEBAPP_PRIVATE.save()
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        self.client.cookies[WEBAPP_SESSION_COOKIE] = session.session_key
        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": "query { me { user { email } } }"}),
            content_type="application/json",
            HTTP_HOST="my-custom-domain.example.com",
            HTTP_ORIGIN="http://my-custom-domain.example.com",
        )
        self.assertEqual(response.status_code, 200)

    def test_webapp_cannot_see_pipeline_in_another_workspace(self):
        # A webapp must be hard-scoped to its own workspace. Even if the
        # session user is also a member of another workspace, the webapp's
        # filter_for_user must not expose data from there.
        other_workspace = Workspace.objects.create(
            name="Other WS", slug="other-ws", db_name="other_ws_db"
        )
        WorkspaceMembership.objects.create(
            user=self.USER,
            workspace=other_workspace,
            role=WorkspaceMembershipRole.ADMIN,
        )
        Pipeline.objects.create(
            workspace=other_workspace, name="Off-Limits", code="off-limits"
        )
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            f'query {{ pipelines(workspaceSlug: "{other_workspace.slug}") {{ items {{ code }} }} }}',
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # The workspace is invisible to the webapp principal so the resolver
        # returns no pipelines — even though the real user can normally see it.
        self.assertEqual(data["data"]["pipelines"]["items"], [])

    def test_empty_allowed_operations_blocks_everything(self):
        webapp = Webapp.objects.create(
            name="No Ops App",
            slug="no-ops-app",
            subdomain="no-ops-app",
            url="http://example.com",
            workspace=self.WORKSPACE,
            created_by=self.USER,
            is_public=False,
            allowed_operations=[],
        )
        session = self._create_webapp_session(webapp, self.USER)
        response = self._graphql_post(
            "no-ops-app",
            "query { me { user { email } } }",
            session_key=session.session_key,
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data["errors"][0]["message"], "Operations not allowed: me")


@override_settings(WEBAPPS_DOMAIN=WEBAPPS_DOMAIN)
class UpdateWebappAllowedOperationsTest(GraphQLTestCase):
    UPDATE_MUTATION = """
        mutation updateWebapp($input: UpdateWebappInput!) {
            updateWebapp(input: $input) {
                success
                errors
                webapp {
                    id
                    allowedOperations
                }
            }
        }
    """

    WEBAPP_QUERY = """
        query webapp($workspaceSlug: String!, $slug: String!) {
            webapp(workspaceSlug: $workspaceSlug, slug: $slug) {
                id
                allowedOperations
            }
        }
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "ops@test.com",
            "password",
            is_superuser=True,
        )
        cls.WORKSPACE = Workspace.objects.create(
            name="Ops WS",
            description="Ops workspace",
        )
        WorkspaceMembership.objects.create(
            user=cls.USER,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )
        cls.WEBAPP = Webapp.objects.create(
            name="Ops Webapp",
            slug="ops-webapp",
            subdomain="ops-webapp",
            url="http://example.com",
            workspace=cls.WORKSPACE,
            created_by=cls.USER,
        )

    def test_update_allowed_operations(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            self.UPDATE_MUTATION,
            {
                "input": {
                    "id": str(self.WEBAPP.id),
                    "allowedOperations": ["PIPELINES_READ", "FILES_READ"],
                }
            },
        )
        self.assertEqual(
            response["data"]["updateWebapp"],
            {
                "success": True,
                "errors": [],
                "webapp": {
                    "id": str(self.WEBAPP.id),
                    "allowedOperations": ["PIPELINES_READ", "FILES_READ"],
                },
            },
        )

    def test_query_returns_allowed_operations(self):
        self.WEBAPP.allowed_operations = [
            Webapp.OperationScope.USER_READ,
            Webapp.OperationScope.FILES_WRITE,
        ]
        self.WEBAPP.save()

        self.client.force_login(self.USER)
        response = self.run_query(
            self.WEBAPP_QUERY,
            {
                "workspaceSlug": self.WORKSPACE.slug,
                "slug": self.WEBAPP.slug,
            },
        )
        self.assertEqual(
            response["data"]["webapp"]["allowedOperations"],
            ["USER_READ", "FILES_WRITE"],
        )

    def test_clear_allowed_operations(self):
        self.WEBAPP.allowed_operations = [Webapp.OperationScope.PIPELINES_READ]
        self.WEBAPP.save()

        self.client.force_login(self.USER)
        response = self.run_query(
            self.UPDATE_MUTATION,
            {
                "input": {
                    "id": str(self.WEBAPP.id),
                    "allowedOperations": [],
                }
            },
        )
        result = response["data"]["updateWebapp"]
        self.assertTrue(result["success"])
        self.assertEqual(result["webapp"]["allowedOperations"], [])

        self.WEBAPP.refresh_from_db()
        self.assertEqual(self.WEBAPP.allowed_operations, [])
