import json

from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase, override_settings

from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import Pipeline
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
