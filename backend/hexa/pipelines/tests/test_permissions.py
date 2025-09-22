from hexa.core.test import TestCase
from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.pipelines.permissions import (
    create_pipeline,
    create_pipeline_version,
    delete_pipeline,
    delete_pipeline_version,
    run_pipeline,
    stop_pipeline,
    update_pipeline,
    update_pipeline_version,
    view_pipeline_version,
)
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class PipelinesOrganizationPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-pipelines",
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
        cls.USER_WORKSPACE_EDITOR = User.objects.create_user(
            "workspace_editor@bluesquarehub.com", "password"
        )
        cls.USER_WORKSPACE_VIEWER = User.objects.create_user(
            "workspace_viewer@bluesquarehub.com", "password"
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
            description="Test workspace for pipeline permissions",
            organization=cls.ORGANIZATION,
        )

        cls.USER_WORKSPACE_ADMIN.is_superuser = False
        cls.USER_WORKSPACE_ADMIN.save()
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_WORKSPACE_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_WORKSPACE_VIEWER,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test Pipeline",
            description="Test pipeline for permission testing",
        )

        cls.PIPELINE_VERSION_1 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            name="Version 1",
            zipfile="test-v1.zip",
            config={"version": "1"},
        )
        cls.PIPELINE_VERSION_2 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            name="Version 2",
            zipfile="test-v2.zip",
            config={"version": "2"},
        )

    def test_organization_owner_can_create_pipeline(self):
        """Organization owners should be able to create pipelines even without workspace membership"""
        self.assertTrue(create_pipeline(self.USER_ORG_OWNER, self.WORKSPACE))

    def test_organization_admin_can_create_pipeline(self):
        """Organization admins should be able to create pipelines even without workspace membership"""
        self.assertTrue(create_pipeline(self.USER_ORG_ADMIN, self.WORKSPACE))

    def test_organization_member_cannot_create_pipeline(self):
        """Organization members should NOT be able to create pipelines without workspace membership"""
        self.assertFalse(create_pipeline(self.USER_ORG_MEMBER, self.WORKSPACE))

    def test_non_organization_member_cannot_create_pipeline(self):
        """Non-organization members should NOT be able to create pipelines without workspace membership"""
        self.assertFalse(create_pipeline(self.USER_NON_ORG_MEMBER, self.WORKSPACE))

    def test_workspace_admin_can_create_pipeline(self):
        """Workspace admins should be able to create pipelines through workspace membership"""
        self.assertTrue(create_pipeline(self.USER_WORKSPACE_ADMIN, self.WORKSPACE))

    def test_workspace_editor_can_create_pipeline(self):
        """Workspace editors should be able to create pipelines through workspace membership"""
        self.assertTrue(create_pipeline(self.USER_WORKSPACE_EDITOR, self.WORKSPACE))

    def test_organization_owner_can_update_pipeline(self):
        """Organization owners should be able to update pipelines even without workspace membership"""
        self.assertTrue(update_pipeline(self.USER_ORG_OWNER, self.PIPELINE))

    def test_organization_admin_can_update_pipeline(self):
        """Organization admins should be able to update pipelines even without workspace membership"""
        self.assertTrue(update_pipeline(self.USER_ORG_ADMIN, self.PIPELINE))

    def test_organization_member_cannot_update_pipeline(self):
        """Organization members should NOT be able to update pipelines without workspace membership"""
        self.assertFalse(update_pipeline(self.USER_ORG_MEMBER, self.PIPELINE))

    def test_non_organization_member_cannot_update_pipeline(self):
        """Non-organization members should NOT be able to update pipelines without workspace membership"""
        self.assertFalse(update_pipeline(self.USER_NON_ORG_MEMBER, self.PIPELINE))

    def test_workspace_admin_can_update_pipeline(self):
        """Workspace admins should be able to update pipelines through workspace membership"""
        self.assertTrue(update_pipeline(self.USER_WORKSPACE_ADMIN, self.PIPELINE))

    def test_workspace_editor_can_update_pipeline(self):
        """Workspace editors should be able to update pipelines through workspace membership"""
        self.assertTrue(update_pipeline(self.USER_WORKSPACE_EDITOR, self.PIPELINE))

    def test_organization_owner_can_delete_pipeline(self):
        """Organization owners should be able to delete pipelines even without workspace membership"""
        self.assertTrue(delete_pipeline(self.USER_ORG_OWNER, self.PIPELINE))

    def test_organization_admin_can_delete_pipeline(self):
        """Organization admins should be able to delete pipelines even without workspace membership"""
        self.assertTrue(delete_pipeline(self.USER_ORG_ADMIN, self.PIPELINE))

    def test_organization_member_cannot_delete_pipeline(self):
        """Organization members should NOT be able to delete pipelines without workspace membership"""
        self.assertFalse(delete_pipeline(self.USER_ORG_MEMBER, self.PIPELINE))

    def test_non_organization_member_cannot_delete_pipeline(self):
        """Non-organization members should NOT be able to delete pipelines without workspace membership"""
        self.assertFalse(delete_pipeline(self.USER_NON_ORG_MEMBER, self.PIPELINE))

    def test_workspace_admin_can_delete_pipeline(self):
        """Workspace admins should be able to delete pipelines through workspace membership"""
        self.assertTrue(delete_pipeline(self.USER_WORKSPACE_ADMIN, self.PIPELINE))

    def test_workspace_editor_cannot_delete_pipeline(self):
        """Workspace editors should NOT be able to delete pipelines (only admins can delete)"""
        self.assertFalse(delete_pipeline(self.USER_WORKSPACE_EDITOR, self.PIPELINE))

    def test_organization_owner_can_run_pipeline(self):
        """Organization owners should be able to run pipelines even without workspace membership"""
        self.assertTrue(run_pipeline(self.USER_ORG_OWNER, self.PIPELINE))

    def test_organization_admin_can_run_pipeline(self):
        """Organization admins should be able to run pipelines even without workspace membership"""
        self.assertTrue(run_pipeline(self.USER_ORG_ADMIN, self.PIPELINE))

    def test_organization_member_cannot_run_pipeline(self):
        """Organization members should NOT be able to run pipelines without workspace membership"""
        self.assertFalse(run_pipeline(self.USER_ORG_MEMBER, self.PIPELINE))

    def test_non_organization_member_cannot_run_pipeline(self):
        """Non-organization members should NOT be able to run pipelines without workspace membership"""
        self.assertFalse(run_pipeline(self.USER_NON_ORG_MEMBER, self.PIPELINE))

    def test_workspace_viewer_can_run_pipeline(self):
        """Workspace viewers should be able to run pipelines through workspace membership"""
        self.assertTrue(run_pipeline(self.USER_WORKSPACE_VIEWER, self.PIPELINE))

    def test_organization_owner_can_stop_pipeline(self):
        """Organization owners should be able to stop pipelines even without workspace membership"""
        self.assertTrue(stop_pipeline(self.USER_ORG_OWNER, self.PIPELINE))

    def test_organization_admin_can_stop_pipeline(self):
        """Organization admins should be able to stop pipelines even without workspace membership"""
        self.assertTrue(stop_pipeline(self.USER_ORG_ADMIN, self.PIPELINE))

    def test_organization_member_cannot_stop_pipeline(self):
        """Organization members should NOT be able to stop pipelines without workspace membership"""
        self.assertFalse(stop_pipeline(self.USER_ORG_MEMBER, self.PIPELINE))

    def test_non_organization_member_cannot_stop_pipeline(self):
        """Non-organization members should NOT be able to stop pipelines without workspace membership"""
        self.assertFalse(stop_pipeline(self.USER_NON_ORG_MEMBER, self.PIPELINE))

    def test_workspace_admin_can_stop_pipeline(self):
        """Workspace admins should be able to stop pipelines through workspace membership"""
        self.assertTrue(stop_pipeline(self.USER_WORKSPACE_ADMIN, self.PIPELINE))

    def test_workspace_editor_can_stop_pipeline(self):
        """Workspace editors should be able to stop pipelines through workspace membership"""
        self.assertTrue(stop_pipeline(self.USER_WORKSPACE_EDITOR, self.PIPELINE))

    def test_workspace_viewer_cannot_stop_pipeline(self):
        """Workspace viewers should NOT be able to stop pipelines (only editors and admins)"""
        self.assertFalse(stop_pipeline(self.USER_WORKSPACE_VIEWER, self.PIPELINE))

    def test_organization_owner_can_create_pipeline_version(self):
        """Organization owners should be able to create pipeline versions even without workspace membership"""
        self.assertTrue(create_pipeline_version(self.USER_ORG_OWNER, self.PIPELINE))

    def test_organization_admin_can_create_pipeline_version(self):
        """Organization admins should be able to create pipeline versions even without workspace membership"""
        self.assertTrue(create_pipeline_version(self.USER_ORG_ADMIN, self.PIPELINE))

    def test_organization_member_cannot_create_pipeline_version(self):
        """Organization members should NOT be able to create pipeline versions without workspace membership"""
        self.assertFalse(create_pipeline_version(self.USER_ORG_MEMBER, self.PIPELINE))

    def test_non_organization_member_cannot_create_pipeline_version(self):
        """Non-organization members should NOT be able to create pipeline versions without workspace membership"""
        self.assertFalse(
            create_pipeline_version(self.USER_NON_ORG_MEMBER, self.PIPELINE)
        )

    def test_workspace_admin_can_create_pipeline_version(self):
        """Workspace admins should be able to create pipeline versions through workspace membership"""
        self.assertTrue(
            create_pipeline_version(self.USER_WORKSPACE_ADMIN, self.PIPELINE)
        )

    def test_workspace_editor_can_create_pipeline_version(self):
        """Workspace editors should be able to create pipeline versions through workspace membership"""
        self.assertTrue(
            create_pipeline_version(self.USER_WORKSPACE_EDITOR, self.PIPELINE)
        )

    def test_organization_owner_can_update_pipeline_version(self):
        """Organization owners should be able to update pipeline versions even without workspace membership"""
        self.assertTrue(
            update_pipeline_version(self.USER_ORG_OWNER, self.PIPELINE_VERSION_1)
        )

    def test_organization_admin_can_update_pipeline_version(self):
        """Organization admins should be able to update pipeline versions even without workspace membership"""
        self.assertTrue(
            update_pipeline_version(self.USER_ORG_ADMIN, self.PIPELINE_VERSION_1)
        )

    def test_organization_member_cannot_update_pipeline_version(self):
        """Organization members should NOT be able to update pipeline versions without workspace membership"""
        self.assertFalse(
            update_pipeline_version(self.USER_ORG_MEMBER, self.PIPELINE_VERSION_1)
        )

    def test_non_organization_member_cannot_update_pipeline_version(self):
        """Non-organization members should NOT be able to update pipeline versions without workspace membership"""
        self.assertFalse(
            update_pipeline_version(self.USER_NON_ORG_MEMBER, self.PIPELINE_VERSION_1)
        )

    def test_workspace_admin_can_update_pipeline_version(self):
        """Workspace admins should be able to update pipeline versions through workspace membership"""
        self.assertTrue(
            update_pipeline_version(self.USER_WORKSPACE_ADMIN, self.PIPELINE_VERSION_1)
        )

    def test_workspace_editor_can_update_pipeline_version(self):
        """Workspace editors should be able to update pipeline versions through workspace membership"""
        self.assertTrue(
            update_pipeline_version(self.USER_WORKSPACE_EDITOR, self.PIPELINE_VERSION_1)
        )

    def test_organization_owner_can_delete_pipeline_version(self):
        """Organization owners should be able to delete pipeline versions even without workspace membership"""
        self.assertTrue(
            delete_pipeline_version(self.USER_ORG_OWNER, self.PIPELINE_VERSION_1)
        )

    def test_organization_admin_can_delete_pipeline_version(self):
        """Organization admins should be able to delete pipeline versions even without workspace membership"""
        self.assertTrue(
            delete_pipeline_version(self.USER_ORG_ADMIN, self.PIPELINE_VERSION_1)
        )

    def test_organization_member_cannot_delete_pipeline_version(self):
        """Organization members should NOT be able to delete pipeline versions without workspace membership"""
        self.assertFalse(
            delete_pipeline_version(self.USER_ORG_MEMBER, self.PIPELINE_VERSION_1)
        )

    def test_non_organization_member_cannot_delete_pipeline_version(self):
        """Non-organization members should NOT be able to delete pipeline versions without workspace membership"""
        self.assertFalse(
            delete_pipeline_version(self.USER_NON_ORG_MEMBER, self.PIPELINE_VERSION_1)
        )

    def test_workspace_admin_can_delete_pipeline_version(self):
        """Workspace admins should be able to delete pipeline versions through workspace membership"""
        self.assertTrue(
            delete_pipeline_version(self.USER_WORKSPACE_ADMIN, self.PIPELINE_VERSION_1)
        )

    def test_workspace_editor_can_delete_pipeline_version(self):
        """Workspace editors should be able to delete pipeline versions through workspace membership"""
        self.assertTrue(
            delete_pipeline_version(self.USER_WORKSPACE_EDITOR, self.PIPELINE_VERSION_1)
        )

    def test_organization_owner_can_view_pipeline_version(self):
        """Organization owners should be able to view pipeline versions even without workspace membership"""
        self.assertTrue(
            view_pipeline_version(self.USER_ORG_OWNER, self.PIPELINE_VERSION_1)
        )

    def test_organization_admin_can_view_pipeline_version(self):
        """Organization admins should be able to view pipeline versions even without workspace membership"""
        self.assertTrue(
            view_pipeline_version(self.USER_ORG_ADMIN, self.PIPELINE_VERSION_1)
        )

    def test_organization_member_cannot_view_pipeline_version(self):
        """Organization members should NOT be able to view pipeline versions without workspace membership"""
        self.assertFalse(
            view_pipeline_version(self.USER_ORG_MEMBER, self.PIPELINE_VERSION_1)
        )

    def test_non_organization_member_cannot_view_pipeline_version(self):
        """Non-organization members should NOT be able to view pipeline versions without workspace membership"""
        self.assertFalse(
            view_pipeline_version(self.USER_NON_ORG_MEMBER, self.PIPELINE_VERSION_1)
        )

    def test_workspace_viewer_can_view_pipeline_version(self):
        """Workspace viewers should be able to view pipeline versions through workspace membership"""
        self.assertTrue(
            view_pipeline_version(self.USER_WORKSPACE_VIEWER, self.PIPELINE_VERSION_1)
        )

    def test_delete_pipeline_version_requires_multiple_versions(self):
        """Cannot delete a pipeline version if it's the only version"""
        single_version_pipeline = Pipeline.objects.create(
            workspace=self.WORKSPACE,
            name="Single Version Pipeline",
            description="Pipeline with only one version",
        )
        single_version = PipelineVersion.objects.create(
            pipeline=single_version_pipeline,
            name="Only Version",
            zipfile="only-version.zip",
            config={"version": "only"},
        )

        # Even organization owners/admins cannot delete the only version
        self.assertFalse(delete_pipeline_version(self.USER_ORG_OWNER, single_version))
        self.assertFalse(delete_pipeline_version(self.USER_ORG_ADMIN, single_version))
        self.assertFalse(
            delete_pipeline_version(self.USER_WORKSPACE_ADMIN, single_version)
        )

    def test_permissions_with_null_organization(self):
        """Test permissions when workspace has no organization"""
        workspace_no_org = Workspace.objects.create_if_has_perm(
            self.USER_WORKSPACE_ADMIN,
            name="No Org Workspace",
            description="Workspace without organization",
            organization=None,
        )

        pipeline_no_org = Pipeline.objects.create(
            workspace=workspace_no_org,
            name="Pipeline No Org",
            description="Pipeline in workspace without organization",
        )

        version_no_org = PipelineVersion.objects.create(
            pipeline=pipeline_no_org,
            name="Version No Org",
            zipfile="no-org.zip",
            config={"version": "no-org"},
        )

        # Organization admin/owner should not have permissions for pipelines in workspace without organization
        self.assertFalse(create_pipeline(self.USER_ORG_OWNER, workspace_no_org))
        self.assertFalse(create_pipeline(self.USER_ORG_ADMIN, workspace_no_org))
        self.assertFalse(update_pipeline(self.USER_ORG_OWNER, pipeline_no_org))
        self.assertFalse(update_pipeline(self.USER_ORG_ADMIN, pipeline_no_org))
        self.assertFalse(delete_pipeline(self.USER_ORG_OWNER, pipeline_no_org))
        self.assertFalse(delete_pipeline(self.USER_ORG_ADMIN, pipeline_no_org))
        self.assertFalse(run_pipeline(self.USER_ORG_OWNER, pipeline_no_org))
        self.assertFalse(run_pipeline(self.USER_ORG_ADMIN, pipeline_no_org))
        self.assertFalse(stop_pipeline(self.USER_ORG_OWNER, pipeline_no_org))
        self.assertFalse(stop_pipeline(self.USER_ORG_ADMIN, pipeline_no_org))
        self.assertFalse(create_pipeline_version(self.USER_ORG_OWNER, pipeline_no_org))
        self.assertFalse(create_pipeline_version(self.USER_ORG_ADMIN, pipeline_no_org))
        self.assertFalse(update_pipeline_version(self.USER_ORG_OWNER, version_no_org))
        self.assertFalse(update_pipeline_version(self.USER_ORG_ADMIN, version_no_org))
        self.assertFalse(view_pipeline_version(self.USER_ORG_OWNER, version_no_org))
        self.assertFalse(view_pipeline_version(self.USER_ORG_ADMIN, version_no_org))

        # Only workspace members should have permissions
        self.assertTrue(create_pipeline(self.USER_WORKSPACE_ADMIN, workspace_no_org))
        self.assertTrue(update_pipeline(self.USER_WORKSPACE_ADMIN, pipeline_no_org))
        self.assertTrue(delete_pipeline(self.USER_WORKSPACE_ADMIN, pipeline_no_org))
        self.assertTrue(run_pipeline(self.USER_WORKSPACE_ADMIN, pipeline_no_org))
        self.assertTrue(stop_pipeline(self.USER_WORKSPACE_ADMIN, pipeline_no_org))
        self.assertTrue(
            create_pipeline_version(self.USER_WORKSPACE_ADMIN, pipeline_no_org)
        )
        self.assertTrue(
            update_pipeline_version(self.USER_WORKSPACE_ADMIN, version_no_org)
        )
        self.assertTrue(
            view_pipeline_version(self.USER_WORKSPACE_ADMIN, version_no_org)
        )
