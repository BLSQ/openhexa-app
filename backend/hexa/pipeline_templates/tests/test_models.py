from django.db.utils import IntegrityError

from hexa.core.test import TestCase
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import Pipeline, PipelineVersion
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


class PipelineTemplateModelTest(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(
            name="Test Workspace", slug="test-workspace", db_name="test_workspace"
        )
        self.other_workspace = Workspace.objects.create(
            name="Test Workspace2", slug="test-workspace2", db_name="test_workspace2"
        )
        self.pipeline = Pipeline.objects.create(
            name="Test Pipeline", workspace=self.workspace
        )
        self.pipeline_version1 = PipelineVersion.objects.create(
            pipeline=self.pipeline, version_number=1
        )
        self.pipeline_version3 = PipelineVersion.objects.create(
            pipeline=self.pipeline, version_number=3
        )

    def test_create_template(self):
        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.code, "test_code")
        self.assertEqual(template.workspace, self.workspace)
        self.assertEqual(template.source_pipeline, self.pipeline)

    def test_unique_template_code_per_workspace(self):
        unique_code = "unique_code"
        PipelineTemplate.objects.create(
            name="Template 1",
            code=unique_code,
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        with self.assertRaises(IntegrityError):
            PipelineTemplate.objects.create(
                name="Template 2",
                code=unique_code,
                workspace=self.workspace,
                source_pipeline=self.pipeline,
            )

    def test_unique_template_name_across_all_workspaces(self):
        unique_name = "Unique Template"
        PipelineTemplate.objects.create(
            name=unique_name,
            code="code1",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        with self.assertRaises(IntegrityError):
            PipelineTemplate.objects.create(
                name=unique_name,
                code="code2",
                workspace=self.other_workspace,
                source_pipeline=self.pipeline,
            )

    def test_create_template_version(self):
        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        template_version1 = template.create_version(self.pipeline_version1)
        self.assertEqual(template_version1.version_number, 1)
        self.assertEqual(template_version1.template, template)
        self.assertEqual(
            template_version1.source_pipeline_version, self.pipeline_version1
        )

        template_version2 = template.create_version(self.pipeline_version3)
        self.assertEqual(template_version2.version_number, 2)
        self.assertEqual(template_version2.template, template)
        self.assertEqual(
            template_version2.source_pipeline_version, self.pipeline_version3
        )

        self.assertEqual(template.versions.count(), 2)


class PipelineTemplateVersionModelTest(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.pipeline = Pipeline.objects.create(
            name="Test Pipeline", workspace=self.workspace
        )
        self.pipeline_version = PipelineVersion.objects.create(
            pipeline=self.pipeline, version_number=1
        )
        self.template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )

    def test_create_template_version(self):
        template_version = PipelineTemplateVersion.objects.create(
            version_number=1,
            template=self.template,
            source_pipeline_version=self.pipeline_version,
        )
        self.assertEqual(template_version.version_number, 1)
        self.assertEqual(template_version.template, self.template)
        self.assertEqual(
            template_version.source_pipeline_version, self.pipeline_version
        )
        self.assertEqual(self.pipeline_version.template_version, template_version)

    def test_unique_template_version_number(self):
        PipelineTemplateVersion.objects.create(
            version_number=1,
            template=self.template,
            source_pipeline_version=self.pipeline_version,
        )
        with self.assertRaises(IntegrityError):
            PipelineTemplateVersion.objects.create(
                version_number=1,
                template=self.template,
                source_pipeline_version=self.pipeline_version,
            )


class PipelineTemplateOrganizationAdminOwnerPermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
            short_name="test-org-template",
            organization_type="CORPORATE",
        )

        cls.ORG_OWNER_USER = User.objects.create_user(
            "owner@bluesquarehub.com", "password"
        )
        cls.ORG_ADMIN_USER = User.objects.create_user(
            "admin@bluesquarehub.com", "password"
        )
        cls.ORG_MEMBER_USER = User.objects.create_user(
            "member@bluesquarehub.com", "password"
        )
        cls.NON_ORG_USER = User.objects.create_user(
            "nonorg@bluesquarehub.com", "password"
        )

        cls.WORKSPACE_ADMIN = User.objects.create_user(
            "workspace_admin@bluesquarehub.com", "password", is_superuser=True
        )

        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_OWNER_USER,
            role=OrganizationMembershipRole.OWNER,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_ADMIN_USER,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.ORG_MEMBER_USER,
            role=OrganizationMembershipRole.MEMBER,
        )

        cls.WORKSPACE_1 = Workspace.objects.create_if_has_perm(
            cls.WORKSPACE_ADMIN,
            name="Workspace 1",
            description="First workspace in organization",
            organization=cls.ORGANIZATION,
        )

        cls.WORKSPACE_2 = Workspace.objects.create_if_has_perm(
            cls.WORKSPACE_ADMIN,
            name="Workspace 2",
            description="Second workspace in organization",
            organization=cls.ORGANIZATION,
        )
        cls.WORKSPACE_ADMIN.is_superuser = False
        cls.WORKSPACE_ADMIN.save()

        cls.PIPELINE_1 = Pipeline.objects.create(
            workspace=cls.WORKSPACE_1,
            name="Pipeline in workspace 1",
            code="pipeline-1",
            description="Pipeline for template 1",
        )

        cls.PIPELINE_2 = Pipeline.objects.create(
            workspace=cls.WORKSPACE_2,
            name="Pipeline in workspace 2",
            code="pipeline-2",
            description="Pipeline for template 2",
        )

        cls.TEMPLATE_1 = PipelineTemplate.objects.create(
            workspace=cls.WORKSPACE_1,
            name="Template in workspace 1",
            code="template-1",
            description="Template in workspace where org admin/owner is not a member",
            source_pipeline=cls.PIPELINE_1,
        )

        cls.TEMPLATE_2 = PipelineTemplate.objects.create(
            workspace=cls.WORKSPACE_2,
            name="Template in workspace 2",
            code="template-2",
            description="Template in another workspace in same org",
            source_pipeline=cls.PIPELINE_2,
        )

    def test_organization_owner_can_access_all_templates_in_organization(self):
        templates = PipelineTemplate.objects.filter_for_user(self.ORG_OWNER_USER)

        self.assertIn(self.TEMPLATE_1, templates)
        self.assertIn(self.TEMPLATE_2, templates)

    def test_organization_admin_can_access_all_templates_in_organization(self):
        templates = PipelineTemplate.objects.filter_for_user(self.ORG_ADMIN_USER)

        self.assertIn(self.TEMPLATE_1, templates)
        self.assertIn(self.TEMPLATE_2, templates)

    def test_organization_member_cannot_access_templates_from_non_member_workspaces(
        self,
    ):
        templates = PipelineTemplate.objects.filter_for_user(self.ORG_MEMBER_USER)

        self.assertNotIn(self.TEMPLATE_1, templates)
        self.assertNotIn(self.TEMPLATE_2, templates)

    def test_non_organization_member_cannot_access_organization_templates(self):
        templates = PipelineTemplate.objects.filter_for_user(self.NON_ORG_USER)

        self.assertNotIn(self.TEMPLATE_1, templates)
        self.assertNotIn(self.TEMPLATE_2, templates)

    def test_organization_admin_owner_access_combined_with_workspace_membership(self):
        WorkspaceMembership.objects.create(
            workspace=self.WORKSPACE_1,
            user=self.ORG_ADMIN_USER,
            role=WorkspaceMembershipRole.VIEWER,
        )

        templates = PipelineTemplate.objects.filter_for_user(self.ORG_ADMIN_USER)

        self.assertIn(self.TEMPLATE_1, templates)
        self.assertIn(self.TEMPLATE_2, templates)
