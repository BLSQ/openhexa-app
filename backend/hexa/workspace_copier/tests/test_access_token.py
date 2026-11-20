from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken

from hexa.core.middlewares import oauth2_token_authentication_middleware
from hexa.oauth.scopes import MCP_SCOPE, WORKSPACE_COPY_SCOPE
from hexa.user_management.models import (
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspace_copier.models import WorkspaceCopyRun, WorkspaceCopyRunStatus
from hexa.workspace_copier.queue import (
    REFUSAL_MESSAGES,
    CopyAlreadyRunning,
    execute_copy_run,
    fail_interrupted_runs,
    queue_duplicate_workspace,
)
from hexa.workspace_copier.results import CopyResult
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
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
        OrganizationMembership.objects.create(
            organization=cls.WORKSPACE.organization,
            user=cls.USER,
            role=OrganizationMembershipRole.MEMBER,
        )
        cls.MEMBERSHIP = WorkspaceMembership.objects.create(
            user=cls.USER, workspace=cls.WORKSPACE, role=WorkspaceMembershipRole.EDITOR
        )

    def queue(self, **overrides):
        options = {
            "name": "Copy",
            "countries": None,
            "resources": ["files"],
            "include_connection_secrets": True,
        }
        options.update(overrides)
        return queue_duplicate_workspace(self.USER, self.WORKSPACE, **options)

    def test_no_token_exists_while_the_run_is_queued(self):
        self.queue()

        self.assertFalse(AccessToken.objects.exists())

    @patch("hexa.workspace_copier.queue.run_copy")
    def test_the_run_gets_a_token_when_it_starts_then_revokes_it(self, mock_run_copy):
        seen = {}

        def copy(**kwargs):
            token = AccessToken.objects.get(token=kwargs["source_token"])
            seen["token"] = token
            seen["expires_in"] = token.expires - timezone.now()
            return CopyResult()

        mock_run_copy.side_effect = copy
        run = self.queue(countries=["BE"])

        execute_copy_run(str(run.id))

        kwargs = mock_run_copy.call_args.kwargs
        self.assertEqual(kwargs["source_token"], kwargs["target_token"])
        self.assertEqual(self.USER, seen["token"].user)
        self.assertEqual(WORKSPACE_COPY_SCOPE, seen["token"].scope)
        self.assertGreater(seen["expires_in"], timedelta(days=1, hours=23))
        self.assertIsNone(kwargs["source_url"])
        self.assertEqual(("BE",), kwargs["options"].target_countries)
        self.assertEqual(str(self.USER.id), kwargs["options"].created_by_id)
        self.assertTrue(kwargs["options"].same_server)
        run.refresh_from_db()
        self.assertEqual(WorkspaceCopyRunStatus.SUCCESS, run.status)
        self.assertIsNone(run.access_token)
        self.assertFalse(AccessToken.objects.exists())

    @patch("hexa.workspace_copier.queue.run_copy")
    def test_a_requester_who_lost_access_while_queued_is_refused(self, mock_run_copy):
        run = self.queue()
        self.MEMBERSHIP.role = WorkspaceMembershipRole.VIEWER
        self.MEMBERSHIP.save()

        execute_copy_run(str(run.id))

        mock_run_copy.assert_not_called()
        run.refresh_from_db()
        self.assertEqual(WorkspaceCopyRunStatus.FAILED, run.status)
        self.assertEqual(REFUSAL_MESSAGES["PERMISSION_DENIED"], run.error)
        self.assertIn(REFUSAL_MESSAGES["PERMISSION_DENIED"], run.logs)
        self.assertFalse(AccessToken.objects.exists())

    @patch("hexa.workspace_copier.queue.run_copy", side_effect=RuntimeError("boom"))
    def test_a_failed_run_revokes_its_token(self, _):
        run = self.queue()

        execute_copy_run(str(run.id))

        run.refresh_from_db()
        self.assertEqual(WorkspaceCopyRunStatus.FAILED, run.status)
        self.assertFalse(AccessToken.objects.exists())

    def test_an_interrupted_run_revokes_its_token(self):
        run = self.queue()
        WorkspaceCopyRun.objects.filter(id=run.id).update(
            status=WorkspaceCopyRunStatus.RUNNING,
            access_token=AccessToken.objects.create(
                user=self.USER,
                token="interrupted",
                scope=WORKSPACE_COPY_SCOPE,
                expires=timezone.now() + timedelta(hours=1),
            ),
        )

        fail_interrupted_runs()

        self.assertFalse(AccessToken.objects.exists())

    def test_a_second_active_run_is_refused(self):
        self.queue()

        with self.assertRaises(CopyAlreadyRunning):
            self.queue()
