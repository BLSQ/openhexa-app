from hexa.core.test import TestCase
from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.data_studio.permissions import (
    create_saved_query,
    delete_saved_query,
    update_saved_query,
    update_saved_query_visibility,
)
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import Workspace

from .testutils import SavedQueryTestMixin


class SavedQueryPermissionsTest(SavedQueryTestMixin, TestCase):
    def _create(self, user, visibility=SavedQueryVisibility.WORKSPACE):
        return self.create_saved_query(user=user, name="q", visibility=visibility)

    def test_create_saved_query(self):
        self.assertTrue(create_saved_query(self.USER_ADMIN, self.WORKSPACE))
        self.assertTrue(create_saved_query(self.USER_EDITOR, self.WORKSPACE))
        self.assertTrue(create_saved_query(self.USER_VIEWER, self.WORKSPACE))
        self.assertFalse(create_saved_query(self.USER_OUTSIDER, self.WORKSPACE))

    def test_update_saved_query(self):
        query = self._create(self.USER_VIEWER)
        # author (a viewer) can update their own query
        self.assertTrue(update_saved_query(self.USER_VIEWER, query))
        # editor/admin can update any shared query in the workspace
        self.assertTrue(update_saved_query(self.USER_EDITOR, query))
        self.assertTrue(update_saved_query(self.USER_ADMIN, query))
        # non-author viewer cannot
        other_viewer_query = self._create(self.USER_EDITOR)
        self.assertFalse(update_saved_query(self.USER_VIEWER, other_viewer_query))
        # outsider cannot
        self.assertFalse(update_saved_query(self.USER_OUTSIDER, query))

    def test_update_private_saved_query(self):
        query = self._create(self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE)
        # the author keeps their rights, no role grants access to anyone else
        self.assertTrue(update_saved_query(self.USER_VIEWER, query))
        self.assertFalse(update_saved_query(self.USER_EDITOR, query))
        self.assertFalse(update_saved_query(self.USER_ADMIN, query))
        self.assertFalse(update_saved_query(self.USER_OUTSIDER, query))

    def test_update_saved_query_visibility(self):
        query = self._create(self.USER_VIEWER)
        self.assertTrue(update_saved_query_visibility(self.USER_VIEWER, query))
        # sharing is the author's call alone, even for members who may edit it
        self.assertFalse(update_saved_query_visibility(self.USER_EDITOR, query))
        self.assertFalse(update_saved_query_visibility(self.USER_ADMIN, query))
        self.assertFalse(update_saved_query_visibility(self.USER_OUTSIDER, query))

    def test_update_saved_query_visibility_without_author(self):
        # created_by is SET_NULL, so an author-less query must not be claimed by
        # whoever comes along.
        query = self._create(self.USER_VIEWER)
        query.created_by = None
        query.save()
        self.assertFalse(update_saved_query_visibility(self.USER_VIEWER, query))
        self.assertFalse(update_saved_query_visibility(self.USER_ADMIN, query))

    def test_delete_saved_query(self):
        query = self._create(self.USER_EDITOR)
        self.assertTrue(delete_saved_query(self.USER_EDITOR, query))
        self.assertTrue(delete_saved_query(self.USER_ADMIN, query))
        self.assertFalse(delete_saved_query(self.USER_VIEWER, query))
        self.assertFalse(delete_saved_query(self.USER_OUTSIDER, query))

    def test_delete_private_saved_query(self):
        query = self._create(self.USER_VIEWER, visibility=SavedQueryVisibility.PRIVATE)
        self.assertTrue(delete_saved_query(self.USER_VIEWER, query))
        self.assertFalse(delete_saved_query(self.USER_EDITOR, query))
        self.assertFalse(delete_saved_query(self.USER_ADMIN, query))


class SavedQueryOrganizationPermissionsTest(TestCase):
    """Org owners/admins can manage saved queries even without workspace membership."""

    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-data-studio",
            organization_type="CORPORATE",
        )
        cls.USER_ORG_OWNER = User.objects.create_user("owner@bluesquarehub.com", "pw")
        cls.USER_ORG_ADMIN = User.objects.create_user(
            "orgadmin@bluesquarehub.com", "pw"
        )
        cls.USER_ORG_MEMBER = User.objects.create_user(
            "orgmember@bluesquarehub.com", "pw"
        )
        cls.USER_NON_MEMBER = User.objects.create_user(
            "nonmember@bluesquarehub.com", "pw"
        )
        cls.USER_WS_CREATOR = User.objects.create_user(
            "wscreator@bluesquarehub.com", "pw", is_superuser=True
        )

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ORG_OWNER,
            role=OrganizationMembershipRole.OWNER,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ORG_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER_ORG_MEMBER,
            role=OrganizationMembershipRole.MEMBER,
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_WS_CREATOR,
            name="Org Workspace",
            description="Test workspace",
            organization=cls.ORGANIZATION,
        )
        cls.USER_WS_CREATOR.is_superuser = False
        cls.USER_WS_CREATOR.save()

        cls.SAVED_QUERY = SavedQuery.objects.create(
            workspace=cls.WORKSPACE,
            created_by=cls.USER_WS_CREATOR,
            name="q",
            content="SELECT 1",
            visibility=SavedQueryVisibility.WORKSPACE,
        )
        cls.PRIVATE_SAVED_QUERY = SavedQuery.objects.create(
            workspace=cls.WORKSPACE,
            created_by=cls.USER_WS_CREATOR,
            name="private q",
            content="SELECT 1",
            visibility=SavedQueryVisibility.PRIVATE,
        )

    def test_create_via_organization_role(self):
        self.assertTrue(create_saved_query(self.USER_ORG_OWNER, self.WORKSPACE))
        self.assertTrue(create_saved_query(self.USER_ORG_ADMIN, self.WORKSPACE))
        self.assertFalse(create_saved_query(self.USER_ORG_MEMBER, self.WORKSPACE))
        self.assertFalse(create_saved_query(self.USER_NON_MEMBER, self.WORKSPACE))

    def test_update_via_organization_role(self):
        self.assertTrue(update_saved_query(self.USER_ORG_OWNER, self.SAVED_QUERY))
        self.assertTrue(update_saved_query(self.USER_ORG_ADMIN, self.SAVED_QUERY))
        self.assertFalse(update_saved_query(self.USER_ORG_MEMBER, self.SAVED_QUERY))
        self.assertFalse(update_saved_query(self.USER_NON_MEMBER, self.SAVED_QUERY))

    def test_delete_via_organization_role(self):
        self.assertTrue(delete_saved_query(self.USER_ORG_OWNER, self.SAVED_QUERY))
        self.assertTrue(delete_saved_query(self.USER_ORG_ADMIN, self.SAVED_QUERY))
        self.assertFalse(delete_saved_query(self.USER_ORG_MEMBER, self.SAVED_QUERY))
        self.assertFalse(delete_saved_query(self.USER_NON_MEMBER, self.SAVED_QUERY))

    def test_organization_role_does_not_reach_private_queries(self):
        # Being an organization admin grants workspace-wide access, not access to
        # somebody's private drafts.
        for user in [self.USER_ORG_OWNER, self.USER_ORG_ADMIN]:
            self.assertFalse(update_saved_query(user, self.PRIVATE_SAVED_QUERY))
            self.assertFalse(delete_saved_query(user, self.PRIVATE_SAVED_QUERY))
            self.assertFalse(
                update_saved_query_visibility(user, self.PRIVATE_SAVED_QUERY)
            )

    def test_organization_role_cannot_change_visibility(self):
        self.assertFalse(
            update_saved_query_visibility(self.USER_ORG_OWNER, self.SAVED_QUERY)
        )
        self.assertFalse(
            update_saved_query_visibility(self.USER_ORG_ADMIN, self.SAVED_QUERY)
        )
        self.assertTrue(
            update_saved_query_visibility(self.USER_WS_CREATOR, self.SAVED_QUERY)
        )

    def test_organization_role_does_not_list_private_queries(self):
        visible = set(SavedQuery.objects.filter_for_user(self.USER_ORG_ADMIN))
        self.assertIn(self.SAVED_QUERY, visible)
        self.assertNotIn(self.PRIVATE_SAVED_QUERY, visible)
