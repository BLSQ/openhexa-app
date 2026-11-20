from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken

from hexa.core.middlewares import oauth2_token_authentication_middleware
from hexa.oauth.scopes import MCP_SCOPE, WORKSPACE_COPY_SCOPE
from hexa.user_management.models import User
from hexa.workspace_copier.models import WorkspaceCopyRun, WorkspaceCopyRunStatus
from hexa.workspace_copier.queue import (
    execute_copy_run,
    fail_interrupted_runs,
    queue_duplicate_workspace,
)
from hexa.workspace_copier.results import CopyResult
from hexa.workspaces.tests.testutils import create_workspace


class CopyTokenAuthenticationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("copy@bluesquarehub.com", "password")

    def token(self, scope=WORKSPACE_COPY_SCOPE, expires_in=timedelta(hours=1)):
        return AccessToken.objects.create(
            user=self.USER,
            token="copy-token",
            scope=scope,
            expires=timezone.now() + expires_in,
        )

    def call(self, path="/graphql/"):
        request = RequestFactory().post(path, HTTP_AUTHORIZATION="Bearer copy-token")
        request.user = AnonymousUser()
        oauth2_token_authentication_middleware(lambda r: r)(request)
        return request.user

    def test_authenticates_graphql_as_the_token_user(self):
        self.token()

        self.assertEqual(self.USER, self.call())

    def test_is_refused_outside_graphql(self):
        self.token()

        self.assertFalse(self.call("/mcp/").is_authenticated)

    def test_an_expired_token_authenticates_nobody(self):
        self.token(expires_in=timedelta(seconds=-1))

        self.assertFalse(self.call().is_authenticated)

    def test_an_mcp_token_does_not_reach_graphql(self):
        self.token(scope=MCP_SCOPE)

        self.assertFalse(self.call().is_authenticated)


class CopyTokenLifecycleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("copy@bluesquarehub.com", "password")
        cls.WORKSPACE = create_workspace(name="Source")

    def queue(self, **overrides):
        options = {
            "name": "Copy",
            "countries": None,
            "resources": ["files"],
            "include_connection_secrets": True,
        }
        options.update(overrides)
        return queue_duplicate_workspace(self.USER, self.WORKSPACE, **options)

    @patch("hexa.workspace_copier.queue.run_copy")
    def test_the_run_copies_with_the_token_then_revokes_it(self, mock_run_copy):
        mock_run_copy.return_value = CopyResult()
        run = self.queue(countries=["BE"])
        raw_token = run.access_token.token

        execute_copy_run(str(run.id))

        kwargs = mock_run_copy.call_args.kwargs
        self.assertEqual(raw_token, kwargs["source_token"])
        self.assertEqual(raw_token, kwargs["target_token"])
        self.assertIsNone(kwargs["source_url"])
        self.assertEqual(("BE",), kwargs["options"].target_countries)
        self.assertTrue(kwargs["options"].same_server)
        run.refresh_from_db()
        self.assertEqual(WorkspaceCopyRunStatus.SUCCESS, run.status)
        self.assertIsNone(run.access_token)
        self.assertFalse(AccessToken.objects.filter(token=raw_token).exists())

    @patch("hexa.workspace_copier.queue.run_copy", side_effect=RuntimeError("boom"))
    def test_a_failed_run_revokes_its_token(self, _):
        run = self.queue()

        execute_copy_run(str(run.id))

        self.assertFalse(AccessToken.objects.exists())

    def test_an_interrupted_run_revokes_its_token(self):
        run = self.queue()
        WorkspaceCopyRun.objects.filter(id=run.id).update(
            status=WorkspaceCopyRunStatus.RUNNING
        )

        fail_interrupted_runs()

        self.assertFalse(AccessToken.objects.exists())

    def test_tokens_of_runs_still_going_are_kept(self):
        self.queue()

        fail_interrupted_runs()

        self.assertEqual(1, AccessToken.objects.count())
