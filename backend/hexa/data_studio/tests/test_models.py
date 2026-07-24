from django.core.exceptions import PermissionDenied

from hexa.core.test import TestCase
from hexa.data_studio.execution import ParameterError
from hexa.data_studio.models import SavedQuery

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

    def test_create_generates_unique_slug(self):
        first = self._create(name="My report")
        second = self._create(name="My report")
        self.assertEqual(first.slug, "my-report")
        self.assertNotEqual(second.slug, first.slug)
        self.assertTrue(second.slug.startswith("my-report-"))

    def test_create_with_parameters(self):
        query = SavedQuery.objects.create_if_has_perm(
            self.USER_EDITOR,
            self.WORKSPACE,
            name="p",
            content="SELECT * FROM demo LIMIT {{ limit }}",
            parameters=[{"name": "limit", "type": "integer", "kind": "value"}],
        )
        self.assertEqual(query.parameters[0]["name"], "limit")

    def test_create_with_invalid_parameters_rejected(self):
        with self.assertRaises(ParameterError):
            SavedQuery.objects.create_if_has_perm(
                self.USER_EDITOR,
                self.WORKSPACE,
                name="p",
                content="SELECT 1",
                parameters=[{"name": "1bad", "type": "string"}],
            )

    def test_create_public_requires_publish_permission(self):
        # Editor cannot publish (admin-only)
        with self.assertRaises(PermissionDenied):
            SavedQuery.objects.create_if_has_perm(
                self.USER_EDITOR,
                self.WORKSPACE,
                name="pub",
                content="SELECT 1",
                is_public=True,
            )
        # Admin can
        query = SavedQuery.objects.create_if_has_perm(
            self.USER_ADMIN,
            self.WORKSPACE,
            name="pub",
            content="SELECT 1",
            is_public=True,
        )
        self.assertTrue(query.is_public)

    def test_update_publish_requires_publish_permission(self):
        query = self._create(user=self.USER_EDITOR)
        # Author (editor) can edit content but not flip is_public
        with self.assertRaises(PermissionDenied):
            query.update_if_has_perm(principal=self.USER_EDITOR, is_public=True)
        query.refresh_from_db()
        self.assertFalse(query.is_public)
        # Admin can publish
        query.update_if_has_perm(principal=self.USER_ADMIN, is_public=True)
        query.refresh_from_db()
        self.assertTrue(query.is_public)

    def test_update_parameters(self):
        query = self._create(user=self.USER_EDITOR)
        query.update_if_has_perm(
            principal=self.USER_EDITOR,
            parameters=[{"name": "limit", "type": "integer", "kind": "value"}],
        )
        query.refresh_from_db()
        self.assertEqual(query.parameters[0]["name"], "limit")
