from hexa.core.test import TestCase
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipeline_templates.permissions import (
    create_pipeline_template_version,
    delete_pipeline_template,
    delete_pipeline_template_version,
    update_pipeline_template,
    update_pipeline_template_version,
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


class PipelineTemplatesOrganizationPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-pipeline-templates",
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
            description="Test workspace for pipeline template permissions",
            organization=cls.ORGANIZATION,
        )

        cls.USER_WORKSPACE_ADMIN.is_superuser = False
        cls.USER_WORKSPACE_ADMIN.save()
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE,
            user=cls.USER_WORKSPACE_EDITOR,
            role=WorkspaceMembershipRole.EDITOR,
        )

        cls.PIPELINE_TEMPLATE = PipelineTemplate.objects.create(
            workspace=cls.WORKSPACE,
            name="Test Pipeline Template",
            description="Test pipeline template for permission testing",
        )

        cls.TEMPLATE_VERSION_1 = PipelineTemplateVersion.objects.create(
            template=cls.PIPELINE_TEMPLATE,
            name="Version 1",
            zipfile="test-v1.zip",
            config={"version": "1"},
        )
        cls.TEMPLATE_VERSION_2 = PipelineTemplateVersion.objects.create(
            template=cls.PIPELINE_TEMPLATE,
            name="Version 2",
            zipfile="test-v2.zip",
            config={"version": "2"},
        )

    def test_organization_owner_can_create_pipeline_template_version(self):
        """Organization owners should be able to create pipeline template versions even without workspace membership"""
        self.assertTrue(
            create_pipeline_template_version(self.USER_ORG_OWNER, self.WORKSPACE)
        )

    def test_organization_admin_can_create_pipeline_template_version(self):
        """Organization admins should be able to create pipeline template versions even without workspace membership"""
        self.assertTrue(
            create_pipeline_template_version(self.USER_ORG_ADMIN, self.WORKSPACE)
        )

    def test_organization_member_cannot_create_pipeline_template_version(self):
        """Organization members should NOT be able to create pipeline template versions without workspace membership"""
        self.assertFalse(
            create_pipeline_template_version(self.USER_ORG_MEMBER, self.WORKSPACE)
        )

    def test_non_organization_member_cannot_create_pipeline_template_version(self):
        """Non-organization members should NOT be able to create pipeline template versions without workspace membership"""
        self.assertFalse(
            create_pipeline_template_version(self.USER_NON_ORG_MEMBER, self.WORKSPACE)
        )

    def test_workspace_admin_can_create_pipeline_template_version(self):
        """Workspace admins should be able to create pipeline template versions through workspace membership"""
        self.assertTrue(
            create_pipeline_template_version(self.USER_WORKSPACE_ADMIN, self.WORKSPACE)
        )

    def test_workspace_editor_can_create_pipeline_template_version(self):
        """Workspace editors should be able to create pipeline template versions through workspace membership"""
        self.assertTrue(
            create_pipeline_template_version(self.USER_WORKSPACE_EDITOR, self.WORKSPACE)
        )

    def test_organization_owner_can_delete_pipeline_template(self):
        """Organization owners should be able to delete pipeline templates even without workspace membership"""
        self.assertTrue(
            delete_pipeline_template(self.USER_ORG_OWNER, self.PIPELINE_TEMPLATE)
        )

    def test_organization_admin_can_delete_pipeline_template(self):
        """Organization admins should be able to delete pipeline templates even without workspace membership"""
        self.assertTrue(
            delete_pipeline_template(self.USER_ORG_ADMIN, self.PIPELINE_TEMPLATE)
        )

    def test_organization_member_cannot_delete_pipeline_template(self):
        """Organization members should NOT be able to delete pipeline templates without workspace membership"""
        self.assertFalse(
            delete_pipeline_template(self.USER_ORG_MEMBER, self.PIPELINE_TEMPLATE)
        )

    def test_non_organization_member_cannot_delete_pipeline_template(self):
        """Non-organization members should NOT be able to delete pipeline templates without workspace membership"""
        self.assertFalse(
            delete_pipeline_template(self.USER_NON_ORG_MEMBER, self.PIPELINE_TEMPLATE)
        )

    def test_workspace_admin_can_delete_pipeline_template(self):
        """Workspace admins should be able to delete pipeline templates through workspace membership"""
        self.assertTrue(
            delete_pipeline_template(self.USER_WORKSPACE_ADMIN, self.PIPELINE_TEMPLATE)
        )

    def test_workspace_editor_cannot_delete_pipeline_template(self):
        """Workspace editors should NOT be able to delete pipeline templates (only admins can delete)"""
        self.assertFalse(
            delete_pipeline_template(self.USER_WORKSPACE_EDITOR, self.PIPELINE_TEMPLATE)
        )

    def test_organization_owner_can_update_pipeline_template(self):
        """Organization owners should be able to update pipeline templates even without workspace membership"""
        self.assertTrue(
            update_pipeline_template(self.USER_ORG_OWNER, self.PIPELINE_TEMPLATE)
        )

    def test_organization_admin_can_update_pipeline_template(self):
        """Organization admins should be able to update pipeline templates even without workspace membership"""
        self.assertTrue(
            update_pipeline_template(self.USER_ORG_ADMIN, self.PIPELINE_TEMPLATE)
        )

    def test_organization_member_cannot_update_pipeline_template(self):
        """Organization members should NOT be able to update pipeline templates without workspace membership"""
        self.assertFalse(
            update_pipeline_template(self.USER_ORG_MEMBER, self.PIPELINE_TEMPLATE)
        )

    def test_non_organization_member_cannot_update_pipeline_template(self):
        """Non-organization members should NOT be able to update pipeline templates without workspace membership"""
        self.assertFalse(
            update_pipeline_template(self.USER_NON_ORG_MEMBER, self.PIPELINE_TEMPLATE)
        )

    def test_workspace_admin_can_update_pipeline_template(self):
        """Workspace admins should be able to update pipeline templates through workspace membership"""
        self.assertTrue(
            update_pipeline_template(self.USER_WORKSPACE_ADMIN, self.PIPELINE_TEMPLATE)
        )

    def test_workspace_editor_can_update_pipeline_template(self):
        """Workspace editors should be able to update pipeline templates through workspace membership"""
        self.assertTrue(
            update_pipeline_template(self.USER_WORKSPACE_EDITOR, self.PIPELINE_TEMPLATE)
        )

    def test_organization_owner_can_delete_pipeline_template_version(self):
        """Organization owners should be able to delete pipeline template versions even without workspace membership"""
        self.assertTrue(
            delete_pipeline_template_version(
                self.USER_ORG_OWNER, self.TEMPLATE_VERSION_1
            )
        )

    def test_organization_admin_can_delete_pipeline_template_version(self):
        """Organization admins should be able to delete pipeline template versions even without workspace membership"""
        self.assertTrue(
            delete_pipeline_template_version(
                self.USER_ORG_ADMIN, self.TEMPLATE_VERSION_1
            )
        )

    def test_organization_member_cannot_delete_pipeline_template_version(self):
        """Organization members should NOT be able to delete pipeline template versions without workspace membership"""
        self.assertFalse(
            delete_pipeline_template_version(
                self.USER_ORG_MEMBER, self.TEMPLATE_VERSION_1
            )
        )

    def test_non_organization_member_cannot_delete_pipeline_template_version(self):
        """Non-organization members should NOT be able to delete pipeline template versions without workspace membership"""
        self.assertFalse(
            delete_pipeline_template_version(
                self.USER_NON_ORG_MEMBER, self.TEMPLATE_VERSION_1
            )
        )

    def test_workspace_admin_can_delete_pipeline_template_version(self):
        """Workspace admins should be able to delete pipeline template versions through workspace membership"""
        self.assertTrue(
            delete_pipeline_template_version(
                self.USER_WORKSPACE_ADMIN, self.TEMPLATE_VERSION_1
            )
        )

    def test_workspace_editor_cannot_delete_pipeline_template_version(self):
        """Workspace editors should NOT be able to delete pipeline template versions (only admins can delete)"""
        self.assertFalse(
            delete_pipeline_template_version(
                self.USER_WORKSPACE_EDITOR, self.TEMPLATE_VERSION_1
            )
        )

    def test_organization_owner_can_update_pipeline_template_version(self):
        """Organization owners should be able to update pipeline template versions even without workspace membership"""
        self.assertTrue(
            update_pipeline_template_version(
                self.USER_ORG_OWNER, self.TEMPLATE_VERSION_1
            )
        )

    def test_organization_admin_can_update_pipeline_template_version(self):
        """Organization admins should be able to update pipeline template versions even without workspace membership"""
        self.assertTrue(
            update_pipeline_template_version(
                self.USER_ORG_ADMIN, self.TEMPLATE_VERSION_1
            )
        )

    def test_organization_member_cannot_update_pipeline_template_version(self):
        """Organization members should NOT be able to update pipeline template versions without workspace membership"""
        self.assertFalse(
            update_pipeline_template_version(
                self.USER_ORG_MEMBER, self.TEMPLATE_VERSION_1
            )
        )

    def test_non_organization_member_cannot_update_pipeline_template_version(self):
        """Non-organization members should NOT be able to update pipeline template versions without workspace membership"""
        self.assertFalse(
            update_pipeline_template_version(
                self.USER_NON_ORG_MEMBER, self.TEMPLATE_VERSION_1
            )
        )

    def test_workspace_admin_can_update_pipeline_template_version(self):
        """Workspace admins should be able to update pipeline template versions through workspace membership"""
        self.assertTrue(
            update_pipeline_template_version(
                self.USER_WORKSPACE_ADMIN, self.TEMPLATE_VERSION_1
            )
        )

    def test_workspace_editor_can_update_pipeline_template_version(self):
        """Workspace editors should be able to update pipeline template versions through workspace membership"""
        self.assertTrue(
            update_pipeline_template_version(
                self.USER_WORKSPACE_EDITOR, self.TEMPLATE_VERSION_1
            )
        )

    def test_delete_template_version_requires_multiple_versions(self):
        """Cannot delete a template version if it's the only version"""
        single_version_template = PipelineTemplate.objects.create(
            workspace=self.WORKSPACE,
            name="Single Version Template",
            description="Template with only one version",
        )
        single_version = PipelineTemplateVersion.objects.create(
            template=single_version_template,
            name="Only Version",
            zipfile="only-version.zip",
            config={"version": "only"},
        )

        # Even organization owners/admins cannot delete the only version
        self.assertFalse(
            delete_pipeline_template_version(self.USER_ORG_OWNER, single_version)
        )
        self.assertFalse(
            delete_pipeline_template_version(self.USER_ORG_ADMIN, single_version)
        )
        self.assertFalse(
            delete_pipeline_template_version(self.USER_WORKSPACE_ADMIN, single_version)
        )

    def test_permissions_with_null_organization(self):
        """Test permissions when workspace has no organization"""
        workspace_no_org = Workspace.objects.create_if_has_perm(
            self.USER_WORKSPACE_ADMIN,
            name="No Org Workspace",
            description="Workspace without organization",
            organization=None,
        )

        template_no_org = PipelineTemplate.objects.create(
            workspace=workspace_no_org,
            name="Template No Org",
            description="Template in workspace without organization",
        )

        version_no_org = PipelineTemplateVersion.objects.create(
            template=template_no_org,
            name="Version No Org",
            zipfile="no-org.zip",
            config={"version": "no-org"},
        )

        # Organization admin/owner should not have permissions for templates in workspace without organization
        self.assertFalse(
            create_pipeline_template_version(self.USER_ORG_OWNER, workspace_no_org)
        )
        self.assertFalse(
            create_pipeline_template_version(self.USER_ORG_ADMIN, workspace_no_org)
        )
        self.assertFalse(delete_pipeline_template(self.USER_ORG_OWNER, template_no_org))
        self.assertFalse(delete_pipeline_template(self.USER_ORG_ADMIN, template_no_org))
        self.assertFalse(update_pipeline_template(self.USER_ORG_OWNER, template_no_org))
        self.assertFalse(update_pipeline_template(self.USER_ORG_ADMIN, template_no_org))
        self.assertFalse(
            update_pipeline_template_version(self.USER_ORG_OWNER, version_no_org)
        )
        self.assertFalse(
            update_pipeline_template_version(self.USER_ORG_ADMIN, version_no_org)
        )

        # Only workspace members should have permissions
        self.assertTrue(
            create_pipeline_template_version(
                self.USER_WORKSPACE_ADMIN, workspace_no_org
            )
        )
        self.assertTrue(
            delete_pipeline_template(self.USER_WORKSPACE_ADMIN, template_no_org)
        )
        self.assertTrue(
            update_pipeline_template(self.USER_WORKSPACE_ADMIN, template_no_org)
        )
        self.assertTrue(
            update_pipeline_template_version(self.USER_WORKSPACE_ADMIN, version_no_org)
        )
