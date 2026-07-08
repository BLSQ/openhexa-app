from hexa.core.test import TestCase
from hexa.data_studio.models import SavedQuery
from hexa.data_studio.permissions import (
    create_saved_query,
    delete_saved_query,
    update_saved_query,
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
    def _create(self, user):
        return SavedQuery.objects.create_if_has_perm(
            user, self.WORKSPACE, name="q", content="SELECT 1"
        )

    def test_create_saved_query(self):
        self.assertTrue(create_saved_query(self.USER_ADMIN, self.WORKSPACE))
        self.assertTrue(create_saved_query(self.USER_EDITOR, self.WORKSPACE))
        self.assertTrue(create_saved_query(self.USER_VIEWER, self.WORKSPACE))
        self.assertFalse(create_saved_query(self.USER_OUTSIDER, self.WORKSPACE))

    def test_update_saved_query(self):
        query = self._create(self.USER_VIEWER)
        # author (a viewer) can update their own query
        self.assertTrue(update_saved_query(self.USER_VIEWER, query))
        # editor/admin can update any query in the workspace
        self.assertTrue(update_saved_query(self.USER_EDITOR, query))
        self.assertTrue(update_saved_query(self.USER_ADMIN, query))
        # non-author viewer cannot
        other_viewer_query = self._create(self.USER_EDITOR)
        self.assertFalse(update_saved_query(self.USER_VIEWER, other_viewer_query))
        # outsider cannot
        self.assertFalse(update_saved_query(self.USER_OUTSIDER, query))

    def test_delete_saved_query(self):
        query = self._create(self.USER_EDITOR)
        self.assertTrue(delete_saved_query(self.USER_EDITOR, query))
        self.assertTrue(delete_saved_query(self.USER_ADMIN, query))
        self.assertFalse(delete_saved_query(self.USER_VIEWER, query))
        self.assertFalse(delete_saved_query(self.USER_OUTSIDER, query))


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
