from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from hexa.core.test import TestCase
from hexa.data_studio.models import QueryLog, SavedQuery
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRun
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

from .testutils import SavedQueryTestMixin


class SavedQueryModelTest(SavedQueryTestMixin, TestCase):
    def _create(self, user=None, workspace=None, name="My query"):
        return SavedQuery.objects.create_if_has_perm(
            user or self.USER_EDITOR,
            workspace or self.WORKSPACE,
            name=name,
            content="SELECT 1",
            description="a query",
        )

    def test_create_if_has_perm(self):
        saved_query = self._create(user=self.USER_EDITOR)
        self.assertEqual(saved_query.name, "My query")
        self.assertEqual(saved_query.content, "SELECT 1")
        self.assertEqual(saved_query.created_by, self.USER_EDITOR)
        self.assertEqual(saved_query.workspace, self.WORKSPACE)

    def test_create_any_member_allowed(self):
        # Even a viewer can save a query (consistent with running queries)
        saved_query = self._create(user=self.USER_VIEWER)
        self.assertEqual(saved_query.created_by, self.USER_VIEWER)

    def test_create_non_member_denied(self):
        with self.assertRaises(PermissionDenied):
            self._create(user=self.USER_OUTSIDER)

    def test_filter_for_user_scoped_to_membership(self):
        query_ws1 = self._create(user=self.USER_EDITOR, workspace=self.WORKSPACE)
        query_ws2 = self._create(user=self.USER_ADMIN, workspace=self.WORKSPACE_2)

        # Editor only belongs to WORKSPACE
        self.assertEqual(
            list(SavedQuery.objects.filter_for_user(self.USER_EDITOR)),
            [query_ws1],
        )
        # Admin belongs to both workspaces -> sees both (shared with all members)
        self.assertCountEqual(
            list(SavedQuery.objects.filter_for_user(self.USER_ADMIN)),
            [query_ws1, query_ws2],
        )
        # Outsider sees nothing
        self.assertEqual(
            list(SavedQuery.objects.filter_for_user(self.USER_OUTSIDER)),
            [],
        )

    def test_viewer_sees_shared_queries(self):
        query = self._create(user=self.USER_EDITOR)
        self.assertIn(query, SavedQuery.objects.filter_for_user(self.USER_VIEWER))

    def test_update_by_author(self):
        query = self._create(user=self.USER_VIEWER)
        query.update_if_has_perm(principal=self.USER_VIEWER, name="Renamed")
        query.refresh_from_db()
        self.assertEqual(query.name, "Renamed")

    def test_update_by_editor(self):
        query = self._create(user=self.USER_ADMIN)
        query.update_if_has_perm(principal=self.USER_EDITOR, content="SELECT 2")
        query.refresh_from_db()
        self.assertEqual(query.content, "SELECT 2")

    def test_update_by_viewer_non_author_denied(self):
        query = self._create(user=self.USER_EDITOR)
        with self.assertRaises(PermissionDenied):
            query.update_if_has_perm(principal=self.USER_VIEWER, name="Nope")

    def test_delete_by_author(self):
        query = self._create(user=self.USER_VIEWER)
        query.delete_if_has_perm(principal=self.USER_VIEWER)
        self.assertFalse(SavedQuery.objects.filter(id=query.id).exists())

    def test_delete_by_viewer_non_author_denied(self):
        query = self._create(user=self.USER_EDITOR)
        with self.assertRaises(PermissionDenied):
            query.delete_if_has_perm(principal=self.USER_VIEWER)

    def test_content_is_stored_runnable(self):
        # SQL pasted from a chat or a document carries blanks PostgreSQL rejects.
        # Storing them would keep the query broken every time it is reopened.
        query = SavedQuery.objects.create_if_has_perm(
            self.USER_EDITOR,
            self.WORKSPACE,
            name="Pasted query",
            content="SELECT\u00a0id\u200b FROM demo",
        )
        self.assertEqual("SELECT id FROM demo", query.content)

        query.update_if_has_perm(
            principal=self.USER_EDITOR, content="SELECT\u00a0label FROM demo"
        )
        query.refresh_from_db()
        self.assertEqual("SELECT label FROM demo", query.content)

    def test_content_keeps_literals_verbatim(self):
        # PostgreSQL accepts any character inside a literal, so an exotic blank
        # there is data the user meant to write.
        content = "SELECT 'a\u00a0b' AS x"
        query = SavedQuery.objects.create_if_has_perm(
            self.USER_EDITOR, self.WORKSPACE, name="Literal query", content=content
        )
        self.assertEqual(content, query.content)


class QueryLogModelTest(TestCase):
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
        cls.LOG_WS1_MEMBER = QueryLog.objects.create(
            workspace=cls.WORKSPACE_1,
            user=cls.USER_MEMBER,
            query="SELECT 1",
            status=QueryLog.Status.SUCCESS,
            result_code="00000",
            target="workspace_database",
        )
        cls.LOG_WS1_OTHER_USER = QueryLog.objects.create(
            workspace=cls.WORKSPACE_1,
            user=cls.USER_SUPERUSER,
            query="SELECT 2",
            status=QueryLog.Status.ERROR,
            result_code="42601",
            target="workspace_database",
        )
        cls.LOG_WS2 = QueryLog.objects.create(
            workspace=cls.WORKSPACE_2,
            user=cls.USER_SUPERUSER,
            query="SELECT 3",
            status=QueryLog.Status.SUCCESS,
            result_code="00000",
            target="workspace_database",
        )

    def test_filter_for_user_member_sees_own_workspace_logs(self):
        # Members see all logs of their workspaces, not only their own queries
        self.assertEqual(
            {self.LOG_WS1_MEMBER, self.LOG_WS1_OTHER_USER},
            set(QueryLog.objects.filter_for_user(self.USER_MEMBER)),
        )

    def test_filter_for_user_outsider_sees_nothing(self):
        self.assertEqual(
            0, QueryLog.objects.filter_for_user(self.USER_OUTSIDER).count()
        )

    def test_filter_for_user_anonymous_sees_nothing(self):
        self.assertEqual(0, QueryLog.objects.filter_for_user(AnonymousUser()).count())

    def test_filter_for_user_superuser_sees_everything(self):
        self.assertEqual(
            3, QueryLog.objects.filter_for_user(self.USER_SUPERUSER).count()
        )

    def test_filter_for_user_pipeline_run_user_sees_its_workspace_logs(self):
        pipeline_run = MagicMock(PipelineRun)
        pipeline_run.pipeline = MagicMock(Pipeline)
        pipeline_run.pipeline.workspace = self.WORKSPACE_1
        pipeline_run.pipeline.workspace_id = self.WORKSPACE_1.id
        pipeline_user = PipelineRunUser(pipeline_run)

        self.assertEqual(
            {self.LOG_WS1_MEMBER, self.LOG_WS1_OTHER_USER},
            set(QueryLog.objects.filter_for_user(pipeline_user)),
        )

    def test_log_survives_user_deletion(self):
        # The audit trail must be kept even after the author is deleted
        self.USER_MEMBER.delete()
        self.LOG_WS1_MEMBER.refresh_from_db()
        self.assertIsNone(self.LOG_WS1_MEMBER.user)

    def test_workspace_deletion_removes_logs(self):
        self.WORKSPACE_2.delete()
        self.assertFalse(QueryLog.objects.filter(id=self.LOG_WS2.id).exists())
