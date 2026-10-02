import json

from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase, override_settings

from hexa.pipelines.models import Pipeline
from hexa.user_management.models import User
from hexa.webapps.middlewares import WEBAPP_SESSION_COOKIE, WEBAPP_SESSION_MAX_AGE
from hexa.webapps.models import Webapp
from hexa.workspaces.models import (
    Connection,
    ConnectionField,
    ConnectionType,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.testutils import create_workspace

WEBAPPS_DOMAIN = "webapps.test.local"
SECRET_SENTINEL = "SCOPE-BYPASS-SECRET-SENTINEL"
PIPELINE_SENTINEL = "SCOPE-BYPASS-PIPELINE-SENTINEL"


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
class InlineFragmentBypassTest(WebappProxyClientMixin, TestCase):
    """A web app must not reach fields outside its scopes by wrapping them in
    an inline fragment on the root type.
    """

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
