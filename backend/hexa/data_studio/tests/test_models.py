from unittest.mock import MagicMock, patch

from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import IntegrityError, connection, router, transaction

from hexa.core.test import TestCase
from hexa.data_studio.models import (
    ON_AUTHOR_DELETED,
    QueryLog,
    SavedQuery,
    SavedQueryVisibility,
)
from hexa.pipelines.authentication import PipelineRunUser
from hexa.pipelines.models import Pipeline, PipelineRun
from hexa.user_management.models import User
from hexa.workspaces.models import (
    WorkspaceMembership,
    WorkspaceMembershipRole,
)
from hexa.workspaces.tests.testutils import create_workspace

from .testutils import SavedQueryTestMixin


class SavedQueryModelTest(SavedQueryTestMixin, TestCase):
    def test_create_if_has_perm(self):
        saved_query = self.create_saved_query(user=self.USER_EDITOR)
        self.assertEqual(saved_query.name, "My query")
        self.assertEqual(saved_query.content, "SELECT 1")
        self.assertEqual(saved_query.created_by, self.USER_EDITOR)
        self.assertEqual(saved_query.workspace, self.WORKSPACE)

    def test_create_defaults_to_private(self):
        # A query is the author's until they decide to share it.
        saved_query = SavedQuery.objects.create_if_has_perm(
            self.USER_EDITOR, self.WORKSPACE, name="Draft", content="SELECT 1"
        )
        self.assertEqual(SavedQueryVisibility.PRIVATE, saved_query.visibility)

    def test_create_any_member_allowed(self):
        # Even a viewer can save a query (consistent with running queries)
        saved_query = self.create_saved_query(user=self.USER_VIEWER)
        self.assertEqual(saved_query.created_by, self.USER_VIEWER)

    def test_create_non_member_denied(self):
        with self.assertRaises(PermissionDenied):
            self.create_saved_query(user=self.USER_OUTSIDER)

    def test_filter_for_user_scoped_to_membership(self):
        query_ws1 = self.create_saved_query(
            user=self.USER_EDITOR, workspace=self.WORKSPACE
        )
        query_ws2 = self.create_saved_query(
            user=self.USER_ADMIN, workspace=self.WORKSPACE_2
        )

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
        query = self.create_saved_query(user=self.USER_EDITOR)
        self.assertIn(query, SavedQuery.objects.filter_for_user(self.USER_VIEWER))

    def test_filter_for_user_hides_other_members_private_queries(self):
        mine = self.create_saved_query(
            user=self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE
        )
        theirs = self.create_saved_query(
            user=self.USER_EDITOR, visibility=SavedQueryVisibility.PRIVATE
        )
        shared = self.create_saved_query(user=self.USER_EDITOR)

        self.assertCountEqual(
            [mine, shared],
            list(SavedQuery.objects.filter_for_user(self.USER_VIEWER)),
        )
        self.assertCountEqual(
            [theirs, shared],
            list(SavedQuery.objects.filter_for_user(self.USER_EDITOR)),
        )

    def test_filter_for_user_superuser_sees_private_queries(self):
        private = self.create_saved_query(
            user=self.USER_EDITOR, visibility=SavedQueryVisibility.PRIVATE
        )
        superuser = User.objects.create_user(
            "root@bluesquarehub.com", "rootpassword", is_superuser=True
        )
        self.assertIn(private, SavedQuery.objects.filter_for_user(superuser))

    def test_filter_for_user_anonymous_sees_nothing(self):
        self.create_saved_query(user=self.USER_EDITOR)
        self.assertEqual(0, SavedQuery.objects.filter_for_user(AnonymousUser()).count())

    def test_filter_for_user_pipeline_run_user_only_sees_shared_queries(self):
        # A pipeline run impersonates the workspace, not a person, so it can never
        # be the author of a private query.
        private = self.create_saved_query(
            user=self.USER_EDITOR, visibility=SavedQueryVisibility.PRIVATE
        )
        shared = self.create_saved_query(user=self.USER_EDITOR, name="Shared")

        pipeline_run = MagicMock(PipelineRun)
        pipeline_run.pipeline = MagicMock(Pipeline)
        pipeline_run.pipeline.workspace = self.WORKSPACE
        pipeline_run.pipeline.workspace_id = self.WORKSPACE.id
        visible = set(SavedQuery.objects.filter_for_user(PipelineRunUser(pipeline_run)))

        self.assertIn(shared, visible)
        self.assertNotIn(private, visible)

    def test_update_by_author(self):
        query = self.create_saved_query(user=self.USER_VIEWER)
        query.update_if_has_perm(principal=self.USER_VIEWER, name="Renamed")
        query.refresh_from_db()
        self.assertEqual(query.name, "Renamed")

    def test_update_by_editor(self):
        query = self.create_saved_query(user=self.USER_ADMIN)
        query.update_if_has_perm(principal=self.USER_EDITOR, content="SELECT 2")
        query.refresh_from_db()
        self.assertEqual(query.content, "SELECT 2")

    def test_update_by_viewer_non_author_denied(self):
        query = self.create_saved_query(user=self.USER_EDITOR)
        with self.assertRaises(PermissionDenied):
            query.update_if_has_perm(principal=self.USER_VIEWER, name="Nope")

    def test_update_private_query_by_editor_denied(self):
        query = self.create_saved_query(
            user=self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE
        )
        with self.assertRaises(PermissionDenied):
            query.update_if_has_perm(principal=self.USER_EDITOR, name="Nope")

    def test_author_changes_visibility(self):
        query = self.create_saved_query(
            user=self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE
        )
        query.update_if_has_perm(
            principal=self.USER_VIEWER, visibility=SavedQueryVisibility.WORKSPACE
        )
        query.refresh_from_db()
        self.assertEqual(SavedQueryVisibility.WORKSPACE, query.visibility)

    def test_editor_cannot_change_visibility_of_shared_query(self):
        query = self.create_saved_query(user=self.USER_ADMIN)
        with self.assertRaises(PermissionDenied):
            query.update_if_has_perm(
                principal=self.USER_EDITOR, visibility=SavedQueryVisibility.PRIVATE
            )
        query.refresh_from_db()
        self.assertEqual(SavedQueryVisibility.WORKSPACE, query.visibility)

    def test_editor_can_edit_shared_query_echoing_current_visibility(self):
        # A client sending the whole object back must not need the author's rights
        # just because `visibility` is part of the payload.
        query = self.create_saved_query(user=self.USER_ADMIN)
        query.update_if_has_perm(
            principal=self.USER_EDITOR,
            name="Renamed",
            visibility=SavedQueryVisibility.WORKSPACE,
        )
        query.refresh_from_db()
        self.assertEqual("Renamed", query.name)

    def test_delete_by_author(self):
        query = self.create_saved_query(user=self.USER_VIEWER)
        query.delete_if_has_perm(principal=self.USER_VIEWER)
        self.assertFalse(SavedQuery.objects.filter(id=query.id).exists())

    def test_delete_by_viewer_non_author_denied(self):
        query = self.create_saved_query(user=self.USER_EDITOR)
        with self.assertRaises(PermissionDenied):
            query.delete_if_has_perm(principal=self.USER_VIEWER)

    def test_delete_private_query_by_editor_denied(self):
        query = self.create_saved_query(
            user=self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE
        )
        with self.assertRaises(PermissionDenied):
            query.delete_if_has_perm(principal=self.USER_EDITOR)

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

    def test_slug_generated_from_name(self):
        self.assertEqual("my-query", self.create_saved_query(name="My query").slug)

    def test_slug_suffixed_on_collision(self):
        first = self.create_saved_query(name="My query")
        second = self.create_saved_query(name="My query")
        self.assertEqual("my-query", first.slug)
        self.assertNotEqual(first.slug, second.slug)
        self.assertTrue(second.slug.startswith("my-query-"))

    def test_slug_unchanged_on_rename(self):
        # Web apps address a saved query by slug: a rename must not break them.
        query = self.create_saved_query(name="My query")
        query.update_if_has_perm(principal=self.USER_EDITOR, name="Something else")
        query.refresh_from_db()
        self.assertEqual("my-query", query.slug)

    def test_slug_falls_back_when_name_has_nothing_to_slugify(self):
        self.assertEqual("query", self.create_saved_query(name="!@#$%").slug)

    def test_slug_unique_across_workspaces(self):
        # The slug identifies a saved query on its own, so the same name in
        # another workspace has to be suffixed rather than reused.
        first = self.create_saved_query(user=self.USER_ADMIN, workspace=self.WORKSPACE)
        second = self.create_saved_query(
            user=self.USER_ADMIN, workspace=self.WORKSPACE_2
        )
        self.assertNotEqual(first.slug, second.slug)
        self.assertTrue(second.slug.startswith(f"{first.slug}-"))

    def test_slug_generation_gives_up_instead_of_looping(self):
        # Only a slugify that ignores the suffix can collide every time; a real
        # run varies it and settles on the first or second attempt.
        self.create_saved_query(name="My query")

        with (
            patch("hexa.data_studio.models.slugify", return_value="my-query"),
            self.assertRaises(RuntimeError),
        ):
            self.create_saved_query(name="My query")

    def test_content_keeps_literals_verbatim(self):
        # PostgreSQL accepts any character inside a literal, so an exotic blank
        # there is data the user meant to write.
        content = "SELECT 'a\u00a0b' AS x"
        query = SavedQuery.objects.create_if_has_perm(
            self.USER_EDITOR, self.WORKSPACE, name="Literal query", content=content
        )
        self.assertEqual(content, query.content)


class SavedQueryAuthorDeletionTest(SavedQueryTestMixin, TestCase):
    """What saved queries survive the deletion of the account that wrote them.

    Deletion is exercised through `User.delete()` rather than by calling the handler
    directly: it is the ORM wiring - not the partitioning - that decides whether the
    Django admin, a shell or a cascade all get the same behaviour.
    """

    def _create_private(self, user, **kwargs):
        return self.create_saved_query(
            user=user, visibility=SavedQueryVisibility.PRIVATE, **kwargs
        )

    def test_private_queries_go_with_their_author(self):
        query = self._create_private(self.USER_VIEWER)

        self.USER_VIEWER.delete()

        self.assertFalse(SavedQuery.objects.filter(id=query.id).exists())

    def test_shared_queries_outlive_their_author(self):
        # Colleagues, and the webapps and pipelines built on a shared query, must not
        # lose it because its author left.
        query = self.create_saved_query(user=self.USER_EDITOR)

        self.USER_EDITOR.delete()

        query.refresh_from_db()
        self.assertIsNone(query.created_by)

    def test_only_the_deleted_authors_queries_are_affected(self):
        deleted_author_query = self._create_private(self.USER_VIEWER, name="Theirs")
        other_query = self._create_private(self.USER_EDITOR, name="Mine")

        self.USER_VIEWER.delete()

        self.assertEqual(
            [other_query], list(SavedQuery.objects.filter(id=other_query.id))
        )
        self.assertFalse(SavedQuery.objects.filter(id=deleted_author_query.id).exists())

    def test_bulk_deletion_splits_a_mixed_batch(self):
        # Deleting from the Django admin deletes a queryset of users at once, so the
        # handler gets both authors' queries in a single batch.
        private_query = self._create_private(self.USER_VIEWER)
        shared_query = self.create_saved_query(user=self.USER_EDITOR)

        User.objects.filter(id__in=[self.USER_VIEWER.id, self.USER_EDITOR.id]).delete()

        self.assertFalse(SavedQuery.objects.filter(id=private_query.id).exists())
        shared_query.refresh_from_db()
        self.assertIsNone(shared_query.created_by)

    def test_policy_applies_in_every_workspace(self):
        query = self._create_private(self.USER_ADMIN, workspace=self.WORKSPACE)
        query_2 = self._create_private(self.USER_ADMIN, workspace=self.WORKSPACE_2)

        self.USER_ADMIN.delete()

        self.assertFalse(
            SavedQuery.objects.filter(id__in=[query.id, query_2.id]).exists()
        )

    def test_author_without_queries(self):
        self.USER_VIEWER.delete()

        self.assertFalse(User.objects.filter(id=self.USER_VIEWER.id).exists())

    def test_orphaned_shared_query_stays_visible_to_members(self):
        query = self.create_saved_query(user=self.USER_EDITOR)

        self.USER_EDITOR.delete()

        self.assertEqual(
            [query], list(SavedQuery.objects.filter_for_user(self.USER_ADMIN))
        )

    def test_workspace_deletion_removes_every_query(self):
        # The workspace cascade is unconditional: a private query is not kept alive by
        # the workspace it belonged to disappearing.
        private_query = self._create_private(
            self.USER_ADMIN, workspace=self.WORKSPACE_2
        )
        shared_query = self.create_saved_query(
            user=self.USER_ADMIN, workspace=self.WORKSPACE_2, name="Shared"
        )

        self.WORKSPACE_2.delete()

        self.assertFalse(
            SavedQuery.objects.filter(
                id__in=[private_query.id, shared_query.id]
            ).exists()
        )

    def test_private_query_cannot_lose_its_author(self):
        # Nothing can read an author-less private query, so the database refuses to
        # store one rather than let it linger invisible.
        query = self._create_private(self.USER_VIEWER)

        with self.assertRaises(IntegrityError), transaction.atomic():
            SavedQuery.objects.filter(id=query.id).update(created_by=None)

    def test_the_backend_can_defer_constraint_checks(self):
        # The one thing the PRIVATE policy assumes about the database. CASCADE nulls
        # created_by before deleting on backends that cannot defer, which
        # `data_studio_private_query_has_author` rejects - so on such a backend every
        # test above fails with an IntegrityError. The replacement is the six-line
        # handler documented in `saved_queries_on_author_deleted`: collect() with
        # source_attr, and no field update.
        self.assertTrue(connection.features.can_defer_constraint_checks)

    def test_private_queries_are_listed_under_their_author_in_the_admin(self):
        # The confirmation page is the whole UI of this feature - user deletion has no
        # mutation - and it nests what will be deleted under what causes it. Django's
        # CASCADE passes the collector the relation the queries hang from; an
        # equivalent that omits it still deletes them, but lists them at the top level
        # next to the user rather than underneath.
        query = self._create_private(self.USER_VIEWER)
        collector = NestedObjects(using=router.db_for_write(User))

        collector.collect([self.USER_VIEWER])

        self.assertIn(query, collector.edges.get(self.USER_VIEWER, []))

    def test_every_visibility_states_a_policy(self):
        # A visibility added without deciding whether its queries outlive their author
        # would otherwise be handled by whichever branch happens to catch it.
        self.assertEqual(set(SavedQueryVisibility), set(ON_AUTHOR_DELETED))

    def test_unknown_visibility_fails_loudly(self):
        # Choices are not enforced by the database, so the guard - not the schema - is
        # what stops an unmapped visibility from being silently kept or dropped.
        query = self.create_saved_query(user=self.USER_VIEWER)
        SavedQuery.objects.filter(id=query.id).update(visibility="TEAM")

        with self.assertRaises(ImproperlyConfigured):
            self.USER_VIEWER.delete()


class SavedQueryMembershipRemovalTest(SavedQueryTestMixin, TestCase):
    """Losing access to a workspace is not losing the query.

    Nothing deletes saved queries when a membership goes away, and these tests pin
    that absence rather than any code: `hexa.pipelines.signals` already hangs a
    `post_delete` receiver on WorkspaceMembership to clean up after a departing
    member, which is exactly where someone would reach for saved queries next.
    """

    def _revoke_membership(self, user):
        WorkspaceMembership.objects.get(workspace=self.WORKSPACE, user=user).delete()

    def test_private_query_is_hidden_not_deleted(self):
        query = self.create_saved_query(
            user=self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE
        )

        self._revoke_membership(self.USER_VIEWER)

        query.refresh_from_db()
        self.assertEqual(self.USER_VIEWER, query.created_by)
        self.assertFalse(
            SavedQuery.objects.filter_for_user(self.USER_VIEWER)
            .filter(id=query.id)
            .exists()
        )

    def test_rejoining_the_workspace_brings_the_query_back(self):
        query = self.create_saved_query(
            user=self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE
        )

        self._revoke_membership(self.USER_VIEWER)
        # Pinned in the middle, not just at the end: "brings the query back" would
        # hold trivially if revoking the membership had never hidden it.
        self.assertEqual([], list(SavedQuery.objects.filter_for_user(self.USER_VIEWER)))

        WorkspaceMembership.objects.create(
            workspace=self.WORKSPACE,
            user=self.USER_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
        )

        self.assertEqual(
            [query], list(SavedQuery.objects.filter_for_user(self.USER_VIEWER))
        )

    def test_a_hidden_query_still_goes_with_its_deleted_author(self):
        # The half of the promise that survives the other one: a query kept through a
        # membership change is not thereby kept forever.
        query = self.create_saved_query(
            user=self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE
        )
        self._revoke_membership(self.USER_VIEWER)

        self.USER_VIEWER.delete()

        self.assertFalse(SavedQuery.objects.filter(id=query.id).exists())


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
        cls.WORKSPACE_1 = create_workspace(
            cls.USER_SUPERUSER,
            name="Workspace 1",
            description="First workspace",
            countries=[],
        )
        cls.WORKSPACE_2 = create_workspace(
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
