from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser

from hexa.core.test import TestCase
from hexa.databases.models import DatabaseQueryLog
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRun
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class DatabaseQueryLogTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_SUPERUSER = User.objects.create_user(
            "superuser@bluesquarehub.com", "superuserpassword", is_superuser=True
        )
        cls.USER_MEMBER = User.objects.create_user(
            "member@bluesquarehub.com", "memberpassword"
        )
        cls.USER_OUTSIDER = User.objects.create_user(
            "outsider@bluesquarehub.com", "outsiderpassword"
        )
        cls.WORKSPACE_1 = Workspace.objects.create_if_has_perm(
            cls.USER_SUPERUSER,
            name="Workspace 1",
            description="First workspace",
            countries=[],
        )
        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.USER_SUPERUSER,
            name="Workspace 2",
            description="Second workspace",
            countries=[],
        )
        WorkspaceMembership.objects.create(
            user=cls.USER_MEMBER,
            workspace=cls.WORKSPACE_1,
            role=WorkspaceMembershipRole.VIEWER,
        )
        cls.LOG_WS1_MEMBER = DatabaseQueryLog.objects.create(
            workspace=cls.WORKSPACE_1,
            user=cls.USER_MEMBER,
            query="SELECT 1",
            status=DatabaseQueryLog.Status.SUCCESS,
            result_code="00000",
        )
        cls.LOG_WS1_OTHER_USER = DatabaseQueryLog.objects.create(
            workspace=cls.WORKSPACE_1,
            user=cls.USER_SUPERUSER,
            query="SELECT 2",
            status=DatabaseQueryLog.Status.ERROR,
            result_code="42601",
        )
        cls.LOG_WS2 = DatabaseQueryLog.objects.create(
            workspace=cls.WORKSPACE_2,
            user=cls.USER_SUPERUSER,
            query="SELECT 3",
            status=DatabaseQueryLog.Status.SUCCESS,
            result_code="00000",
        )

    def test_filter_for_user_member_sees_own_workspace_logs(self):
        # Members see all logs of their workspaces, not only their own queries
        self.assertEqual(
            {self.LOG_WS1_MEMBER, self.LOG_WS1_OTHER_USER},
            set(DatabaseQueryLog.objects.filter_for_user(self.USER_MEMBER)),
        )

    def test_filter_for_user_outsider_sees_nothing(self):
        self.assertEqual(
            0, DatabaseQueryLog.objects.filter_for_user(self.USER_OUTSIDER).count()
        )

    def test_filter_for_user_anonymous_sees_nothing(self):
        self.assertEqual(
            0, DatabaseQueryLog.objects.filter_for_user(AnonymousUser()).count()
        )

    def test_filter_for_user_superuser_sees_everything(self):
        self.assertEqual(
            3, DatabaseQueryLog.objects.filter_for_user(self.USER_SUPERUSER).count()
        )

    def test_filter_for_user_pipeline_run_user_sees_its_workspace_logs(self):
        pipeline_run = MagicMock(PipelineRun)
        pipeline_run.pipeline = MagicMock(Pipeline)
        pipeline_run.pipeline.workspace = self.WORKSPACE_1
        pipeline_run.pipeline.workspace_id = self.WORKSPACE_1.id
        pipeline_user = PipelineRunUser(pipeline_run)

        self.assertEqual(
            {self.LOG_WS1_MEMBER, self.LOG_WS1_OTHER_USER},
            set(DatabaseQueryLog.objects.filter_for_user(pipeline_user)),
        )

    def test_log_survives_user_deletion(self):
        # The audit trail must be kept even after the author is deleted
        self.USER_MEMBER.delete()
        self.LOG_WS1_MEMBER.refresh_from_db()
        self.assertIsNone(self.LOG_WS1_MEMBER.user)

    def test_workspace_deletion_removes_logs(self):
        self.WORKSPACE_2.delete()
        self.assertFalse(DatabaseQueryLog.objects.filter(id=self.LOG_WS2.id).exists())
