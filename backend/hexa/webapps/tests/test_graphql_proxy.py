import json
from unittest.mock import patch

from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase, override_settings

from hexa.core.test import GraphQLTestCase
from hexa.data_studio.models import QueryLog, SavedQuery, SavedQueryVisibility
from hexa.datasets.models import Dataset, DatasetLink
from hexa.files.backends.base import StorageObject
from hexa.pipelines.models import Pipeline, PipelineRun, PipelineVersion
from hexa.user_management.models import Organization, User
from hexa.webapps.graphql_proxy import extract_top_level_fields
from hexa.webapps.middlewares import WEBAPP_SESSION_COOKIE, WEBAPP_SESSION_MAX_AGE
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.testutils import create_workspace

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
        cls.WORKSPACE = create_workspace(name="Proxy WS")
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

    def test_user_read_cannot_reach_execute_sql(self):
        """`executeSQL` hangs off `Workspace`, which `USER_READ` grants, and the
        proxy only validates top-level fields -- so the endpoint itself has to
        refuse a webapp rather than rely on the scope check.
        """
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            f"""query {{
                workspace(slug: "{self.WORKSPACE.slug}") {{
                    database {{
                        executeSQL(query: "SELECT 1") {{ success errors rows }}
                    }}
                }}
            }}""",
            session_key=session.session_key,
        )
        # The proxy lets the query through (its top-level field is allowed);
        # the refusal comes from the resolver.
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)["data"]["workspace"]["database"][
            "executeSQL"
        ]
        self.assertEqual(
            result, {"success": False, "errors": ["PERMISSION_DENIED"], "rows": None}
        )
        query_log = QueryLog.objects.get(workspace=self.WORKSPACE)
        self.assertEqual(query_log.status, QueryLog.Status.DENIED)
        self.assertEqual(query_log.user, self.USER)

    def _execute_saved_query(self, webapp, subdomain, slug):
        session = self._create_webapp_session(webapp, self.USER)
        return self._graphql_post(
            subdomain,
            f"""query {{
                executeSavedQuery(input: {{ slug: "{slug}" }}) {{
                    success errors rows
                }}
            }}""",
            session_key=session.session_key,
        )

    def _create_saved_query(self, visibility=SavedQueryVisibility.WORKSPACE):
        # Shared by default: a web app authenticates as the workspace rather than
        # as a person, so it only ever reaches WORKSPACE-visibility queries.
        return SavedQuery.objects.create(
            workspace=self.WORKSPACE,
            created_by=self.USER,
            name="Probe",
            content="SELECT 1 AS probe",
            visibility=visibility,
        )

    def test_database_read_scope_runs_a_saved_query(self):
        saved_query = self._create_saved_query()
        webapp = self._create_scoped_webapp(
            "db-app", [Webapp.OperationScope.DATABASE_READ]
        )

        # This class's workspace has no provisioned database (it is created
        # without a principal). What is under test here is the scope gate and
        # how the run is attributed; executing SQL for real is covered in
        # hexa.data_studio.tests.test_schema.
        with patch(
            "hexa.data_studio.query_runner.execute_database_query",
            return_value={
                "columns": ["probe"],
                "rows": [{"probe": 1}],
                "row_count": 1,
                "truncated": False,
                "duration_ms": 1,
            },
        ):
            response = self._execute_saved_query(webapp, "db-app", saved_query.slug)

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)["data"]["executeSavedQuery"]
        self.assertEqual(
            {"success": True, "errors": [], "rows": [{"probe": 1}]}, result
        )
        log = QueryLog.objects.get()
        self.assertEqual(QueryLog.Origin.WEBAPP, log.origin)
        self.assertEqual(saved_query, log.saved_query)
        self.assertEqual(self.USER, log.user)

    def test_private_saved_query_is_out_of_reach(self):
        # A web app authenticates as the workspace, not as the query's author, so
        # a PRIVATE query stays the author's own even with the scope granted.
        saved_query = self._create_saved_query(visibility=SavedQueryVisibility.PRIVATE)
        webapp = self._create_scoped_webapp(
            "db-app", [Webapp.OperationScope.DATABASE_READ]
        )

        response = self._execute_saved_query(webapp, "db-app", saved_query.slug)

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)["data"]["executeSavedQuery"]
        self.assertEqual(["SAVED_QUERY_NOT_FOUND"], result["errors"])
        self.assertEqual(0, QueryLog.objects.count())

    def test_saved_query_needs_the_database_read_scope(self):
        saved_query = self._create_saved_query()

        response = self._execute_saved_query(
            self.WEBAPP_PRIVATE, "private-app", saved_query.slug
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            "executeSavedQuery", json.loads(response.content)["errors"][0]["message"]
        )

    def test_database_read_scope_does_not_expose_the_sql(self):
        """The scope buys execution, not the query text: a web app that could
        read `content` could rewrite the query and run that instead.
        """
        webapp = self._create_scoped_webapp(
            "db-app-2", [Webapp.OperationScope.DATABASE_READ]
        )
        session = self._create_webapp_session(webapp, self.USER)

        lookups = [
            'savedQuery(id: "00000000-0000-0000-0000-000000000000")',
            'savedQueryBySlug(workspaceSlug: "ws", slug: "probe")',
        ]
        for lookup in lookups:
            with self.subTest(lookup=lookup):
                response = self._graphql_post(
                    "db-app-2",
                    f"query {{ {lookup} {{ content }} }}",
                    session_key=session.session_key,
                )
                self.assertEqual(response.status_code, 403)

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

    def test_local_dev_origin_allowed_on_preview_host(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        preview_host = f"{session.session_key}.{WEBAPPS_DOMAIN}"
        self.client.cookies[WEBAPP_SESSION_COOKIE] = session.session_key
        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": "query { me { user { email } } }"}),
            content_type="application/json",
            HTTP_HOST=preview_host,
            HTTP_ORIGIN="http://localhost:5173",
        )
        self.assertEqual(response.status_code, 200)

    def test_null_origin_allowed_on_preview_host(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        preview_host = f"{session.session_key}.{WEBAPPS_DOMAIN}"
        self.client.cookies[WEBAPP_SESSION_COOKIE] = session.session_key
        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": "query { me { user { email } } }"}),
            content_type="application/json",
            HTTP_HOST=preview_host,
            HTTP_ORIGIN="null",
        )
        self.assertEqual(response.status_code, 200)

    def test_local_dev_origin_rejected_on_real_subdomain(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        response = self._graphql_post(
            "private-app",
            "query { me { user { email } } }",
            session_key=session.session_key,
            extra_headers={"HTTP_ORIGIN": "http://localhost:5173"},
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data["errors"][0]["message"], "Origin not allowed")

    def test_preflight_from_local_dev_origin_on_preview_host(self):
        session = self._create_webapp_session(self.WEBAPP_PRIVATE, self.USER)
        preview_host = f"{session.session_key}.{WEBAPPS_DOMAIN}"
        response = self.client.options(
            "/graphql/",
            HTTP_HOST=preview_host,
            HTTP_ORIGIN="http://localhost:5173",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Access-Control-Allow-Origin"], "http://localhost:5173"
        )

    def test_preflight_from_local_dev_origin_on_real_subdomain_has_no_cors(self):
        response = self.client.options(
            "/graphql/",
            HTTP_HOST=f"private-app.{WEBAPPS_DOMAIN}",
            HTTP_ORIGIN="http://localhost:5173",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        self.assertNotIn("Access-Control-Allow-Origin", response)

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
        cls.WORKSPACE = create_workspace(
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


@override_settings(
    WEBAPPS_DOMAIN=WEBAPPS_DOMAIN,
    ALLOWED_HOSTS=["*"],
)
class GraphQLProxyWorkspaceScopingTest(TestCase):
    """End-to-end test that a webapp embedded in workspace A cannot reach
    workspace B's data via the GraphQL proxy, even when the embedding user
    is a member of both workspaces.
    """

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "multi@test.com", "password", is_superuser=True
        )
        cls.ORGANIZATION = Organization.objects.create(name="Proxy Scoping Org")
        cls.WORKSPACE_A = create_workspace(
            cls.USER, name="WS A", organization=cls.ORGANIZATION
        )
        cls.WORKSPACE_B = create_workspace(
            cls.USER, name="WS B", organization=cls.ORGANIZATION
        )
        cls.USER.is_superuser = False
        cls.USER.save()
        cls.WEBAPP_A = Webapp.objects.create(
            name="App A",
            slug="app-a",
            subdomain="app-a",
            url="http://example.com",
            workspace=cls.WORKSPACE_A,
            created_by=cls.USER,
            is_public=False,
            allowed_operations=[Webapp.OperationScope.PIPELINES_READ],
        )
        Pipeline.objects.create(workspace=cls.WORKSPACE_A, name="Pipeline A", code="pa")
        Pipeline.objects.create(workspace=cls.WORKSPACE_B, name="Pipeline B", code="pb")

    def _create_session(self, webapp, user):
        session = SessionStore()
        session.set_expiry(WEBAPP_SESSION_MAX_AGE)
        session["user_id"] = str(user.pk)
        session["webapp_id"] = str(webapp.pk)
        session.create()
        return session

    def _graphql_post(self, subdomain, query, session_key):
        self.client.cookies[WEBAPP_SESSION_COOKIE] = session_key
        return self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
            HTTP_HOST=f"{subdomain}.{WEBAPPS_DOMAIN}",
        )

    def test_proxy_query_against_own_workspace_returns_data(self):
        session = self._create_session(self.WEBAPP_A, self.USER)
        response = self._graphql_post(
            "app-a",
            f'query {{ pipelines(workspaceSlug: "{self.WORKSPACE_A.slug}") {{ items {{ code }} }} }}',
            session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        codes = {
            p["code"]
            for p in json.loads(response.content)["data"]["pipelines"]["items"]
        }
        self.assertEqual(codes, {"pa"})

    def test_proxy_query_against_other_workspace_is_empty(self):
        session = self._create_session(self.WEBAPP_A, self.USER)
        response = self._graphql_post(
            "app-a",
            f'query {{ pipelines(workspaceSlug: "{self.WORKSPACE_B.slug}") {{ items {{ code }} }} }}',
            session.session_key,
        )
        self.assertEqual(response.status_code, 200)
        items = json.loads(response.content)["data"]["pipelines"]["items"]
        self.assertEqual(items, [])

    def test_saved_query_of_other_workspace_is_out_of_reach(self):
        """`executeSavedQuery` takes a slug and no workspace, so nothing in the
        request says which workspace to look in. What keeps a web app to its own
        is `filter_for_user`, which confines a WebappUser to the workspace its
        session was issued for.
        """
        webapp = Webapp.objects.create(
            name="Db App A",
            slug="db-app-a",
            subdomain="db-app-a",
            url="http://example.com",
            workspace=self.WORKSPACE_A,
            created_by=self.USER,
            is_public=False,
            allowed_operations=[Webapp.OperationScope.DATABASE_READ],
        )
        saved_query = SavedQuery.objects.create(
            workspace=self.WORKSPACE_B,
            created_by=self.USER,
            name="B only",
            content="SELECT 1",
            visibility=SavedQueryVisibility.WORKSPACE,
        )
        session = self._create_session(webapp, self.USER)

        response = self._graphql_post(
            "db-app-a",
            f'query {{ executeSavedQuery(input: {{ slug: "{saved_query.slug}" }}) '
            f"{{ success errors }} }}",
            session.session_key,
        )

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)["data"]["executeSavedQuery"]
        self.assertEqual(["SAVED_QUERY_NOT_FOUND"], result["errors"])
        self.assertEqual(0, QueryLog.objects.count())

    def test_non_proxy_graphql_unaffected(self):
        """Hitting the main /graphql/ endpoint (no webapp subdomain) with
        the same user should not be wrapped in WebappUser. The user keeps
        full visibility across their workspaces.
        """
        self.client.force_login(self.USER)
        response = self.client.post(
            "/graphql/",
            data=json.dumps(
                {
                    "query": f'query {{ pipelines(workspaceSlug: "{self.WORKSPACE_B.slug}") {{ items {{ code }} }} }}'
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        codes = {
            p["code"]
            for p in json.loads(response.content)["data"]["pipelines"]["items"]
        }
        self.assertEqual(codes, {"pb"})
