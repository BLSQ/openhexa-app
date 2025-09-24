from hexa.core.test import TestCase
from hexa.datasets.models import Dataset
from hexa.datasets.permissions import (
    create_dataset,
    delete_dataset,
    link_dataset,
    update_dataset,
    view_dataset,
)
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Workspace,
)


class DatasetsOrganizationPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-datasets",
            organization_type="CORPORATE",
        )

        cls.USER_ORG_OWNER = User.objects.create_user(
            "owner@bluesquarehub.com", "password"
        )
        cls.USER_ORG_ADMIN = User.objects.create_user(
            "admin@bluesquarehub.com", "password"
        )
        cls.USER_ORG_MEMBER = User.objects.create_user(
            "member@bluesquarehub.com", "password"
        )
        cls.USER_NON_ORG_MEMBER = User.objects.create_user(
            "non_member@bluesquarehub.com", "password"
        )
        cls.USER_WORKSPACE_ADMIN = User.objects.create_user(
            "workspace_admin@bluesquarehub.com", "password", is_superuser=True
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
            cls.USER_WORKSPACE_ADMIN,
            name="Test Workspace",
            description="Test workspace for datasets permissions",
            organization=cls.ORGANIZATION,
        )

        cls.USER_WORKSPACE_ADMIN.is_superuser = False
        cls.USER_WORKSPACE_ADMIN.save()

        cls.DATASET = Dataset.objects.create(
            name="Test Dataset",
            description="Test dataset for permissions",
            workspace=cls.WORKSPACE,
        )

    def test_organization_owner_can_create_dataset(self):
        """Organization owners should be able to create datasets in workspace even without workspace membership"""
        self.assertTrue(create_dataset(self.USER_ORG_OWNER, self.WORKSPACE))

    def test_organization_admin_can_create_dataset(self):
        """Organization admins should be able to create datasets in workspace even without workspace membership"""
        self.assertTrue(create_dataset(self.USER_ORG_ADMIN, self.WORKSPACE))

    def test_organization_member_cannot_create_dataset(self):
        """Organization members should NOT be able to create datasets through organization membership"""
        self.assertFalse(create_dataset(self.USER_ORG_MEMBER, self.WORKSPACE))

    def test_non_organization_member_cannot_create_dataset(self):
        """Non-organization members should NOT be able to create datasets without workspace membership"""
        self.assertFalse(create_dataset(self.USER_NON_ORG_MEMBER, self.WORKSPACE))

    def test_workspace_admin_can_create_dataset(self):
        """Workspace admins should be able to create datasets through workspace membership"""
        self.assertTrue(create_dataset(self.USER_WORKSPACE_ADMIN, self.WORKSPACE))

    def test_organization_owner_can_update_dataset(self):
        """Organization owners should be able to update datasets in workspace even without workspace membership"""
        self.assertTrue(update_dataset(self.USER_ORG_OWNER, self.DATASET))

    def test_organization_admin_can_update_dataset(self):
        """Organization admins should be able to update datasets in workspace even without workspace membership"""
        self.assertTrue(update_dataset(self.USER_ORG_ADMIN, self.DATASET))

    def test_organization_member_cannot_update_dataset(self):
        """Organization members should NOT be able to update datasets without workspace membership"""
        self.assertFalse(update_dataset(self.USER_ORG_MEMBER, self.DATASET))

    def test_non_organization_member_cannot_update_dataset(self):
        """Non-organization members should NOT be able to update datasets without workspace membership"""
        self.assertFalse(update_dataset(self.USER_NON_ORG_MEMBER, self.DATASET))

    def test_workspace_admin_can_update_dataset(self):
        """Workspace admins should be able to update datasets through workspace membership"""
        self.assertTrue(update_dataset(self.USER_WORKSPACE_ADMIN, self.DATASET))

    def test_organization_owner_can_delete_dataset(self):
        """Organization owners should be able to delete datasets in workspace even without workspace membership"""
        self.assertTrue(delete_dataset(self.USER_ORG_OWNER, self.DATASET))

    def test_organization_admin_can_delete_dataset(self):
        """Organization admins should be able to delete datasets in workspace even without workspace membership"""
        self.assertTrue(delete_dataset(self.USER_ORG_ADMIN, self.DATASET))

    def test_organization_member_cannot_delete_dataset(self):
        """Organization members should NOT be able to delete datasets without workspace membership"""
        self.assertFalse(delete_dataset(self.USER_ORG_MEMBER, self.DATASET))

    def test_non_organization_member_cannot_delete_dataset(self):
        """Non-organization members should NOT be able to delete datasets without workspace membership"""
        self.assertFalse(delete_dataset(self.USER_NON_ORG_MEMBER, self.DATASET))

    def test_workspace_admin_can_delete_dataset(self):
        """Workspace admins should be able to delete datasets through workspace membership"""
        self.assertTrue(delete_dataset(self.USER_WORKSPACE_ADMIN, self.DATASET))

    def test_organization_owner_can_view_dataset(self):
        """Organization owners should be able to view datasets in workspace even without workspace membership"""
        self.assertTrue(view_dataset(self.USER_ORG_OWNER, self.DATASET))

    def test_organization_admin_can_view_dataset(self):
        """Organization admins should be able to view datasets in workspace even without workspace membership"""
        self.assertTrue(view_dataset(self.USER_ORG_ADMIN, self.DATASET))

    def test_organization_member_cannot_view_dataset(self):
        """Organization members should NOT be able to view datasets without workspace membership"""
        self.assertFalse(view_dataset(self.USER_ORG_MEMBER, self.DATASET))

    def test_non_organization_member_cannot_view_dataset(self):
        """Non-organization members should NOT be able to view datasets without workspace membership"""
        self.assertFalse(view_dataset(self.USER_NON_ORG_MEMBER, self.DATASET))

    def test_workspace_admin_can_view_dataset(self):
        """Workspace admins should be able to view datasets through workspace membership"""
        self.assertTrue(view_dataset(self.USER_WORKSPACE_ADMIN, self.DATASET))

    def test_organization_owner_can_link_dataset(self):
        """Organization owners should be able to link datasets to workspace even without workspace membership"""
        self.assertTrue(
            link_dataset(self.USER_ORG_OWNER, (self.DATASET, self.WORKSPACE))
        )

    def test_organization_admin_can_link_dataset(self):
        """Organization admins should be able to link datasets to workspace even without workspace membership"""
        self.assertTrue(
            link_dataset(self.USER_ORG_ADMIN, (self.DATASET, self.WORKSPACE))
        )

    def test_organization_member_cannot_link_dataset(self):
        """Organization members should NOT be able to link datasets without workspace membership"""
        self.assertFalse(
            link_dataset(self.USER_ORG_MEMBER, (self.DATASET, self.WORKSPACE))
        )

    def test_non_organization_member_cannot_link_dataset(self):
        """Non-organization members should NOT be able to link datasets without workspace membership"""
        self.assertFalse(
            link_dataset(self.USER_NON_ORG_MEMBER, (self.DATASET, self.WORKSPACE))
        )

    def test_workspace_admin_can_link_dataset(self):
        """Workspace admins should be able to link datasets through workspace membership"""
        self.assertTrue(
            link_dataset(self.USER_WORKSPACE_ADMIN, (self.DATASET, self.WORKSPACE))
        )

    def test_permissions_with_null_organization(self):
        """Test permissions when workspace has no organization"""
        workspace_no_org = Workspace.objects.create_if_has_perm(
            self.USER_WORKSPACE_ADMIN,
            name="No Org Workspace",
            description="Workspace without organization",
            organization=None,
        )

        dataset_no_org = Dataset.objects.create(
            name="No Org Dataset",
            description="Dataset in workspace without organization",
            workspace=workspace_no_org,
        )

        # Organization admin/owner should not have permissions for workspace without organization
        self.assertFalse(create_dataset(self.USER_ORG_OWNER, workspace_no_org))
        self.assertFalse(create_dataset(self.USER_ORG_ADMIN, workspace_no_org))
        self.assertFalse(update_dataset(self.USER_ORG_OWNER, dataset_no_org))
        self.assertFalse(update_dataset(self.USER_ORG_ADMIN, dataset_no_org))
        self.assertFalse(delete_dataset(self.USER_ORG_OWNER, dataset_no_org))
        self.assertFalse(delete_dataset(self.USER_ORG_ADMIN, dataset_no_org))
        self.assertFalse(view_dataset(self.USER_ORG_OWNER, dataset_no_org))
        self.assertFalse(view_dataset(self.USER_ORG_ADMIN, dataset_no_org))
        self.assertFalse(
            link_dataset(self.USER_ORG_OWNER, (dataset_no_org, workspace_no_org))
        )
        self.assertFalse(
            link_dataset(self.USER_ORG_ADMIN, (dataset_no_org, workspace_no_org))
        )

        # Only workspace member should have permissions
        self.assertTrue(create_dataset(self.USER_WORKSPACE_ADMIN, workspace_no_org))
        self.assertTrue(update_dataset(self.USER_WORKSPACE_ADMIN, dataset_no_org))
        self.assertTrue(delete_dataset(self.USER_WORKSPACE_ADMIN, dataset_no_org))
        self.assertTrue(view_dataset(self.USER_WORKSPACE_ADMIN, dataset_no_org))
        self.assertTrue(
            link_dataset(self.USER_WORKSPACE_ADMIN, (dataset_no_org, workspace_no_org))
        )
