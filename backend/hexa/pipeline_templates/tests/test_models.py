from django.db.utils import IntegrityError

from hexa.core.test import TestCase
from hexa.pipeline_templates.constants import PUBLISHER_BLUESQUARE, PUBLISHER_COMMUNITY
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import Pipeline, PipelineFunctionalType, PipelineVersion
from hexa.tags.models import Tag
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


class PipelineTemplateFunctionalTypeAndTagsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "user_template@bluesquarehub.com", "password", is_superuser=True
        )
        cls.workspace = Workspace.objects.create_if_has_perm(
            cls.user,
            name="Test Template Workspace",
        )
        cls.user.is_superuser = False
        cls.user.save()

        cls.pipeline = Pipeline.objects.create(
            name="Test Pipeline",
            workspace=cls.workspace,
            functional_type=PipelineFunctionalType.EXTRACTION,
        )
        cls.tag1 = Tag.objects.create(name="template-tag1")
        cls.tag2 = Tag.objects.create(name="template-tag2")
        cls.pipeline.tags.set([cls.tag1, cls.tag2])

    def test_template_functional_type_creation(self):
        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
            functional_type=PipelineFunctionalType.TRANSFORMATION,
        )
        self.assertEqual(
            template.functional_type, PipelineFunctionalType.TRANSFORMATION
        )

    def test_template_functional_type_optional(self):
        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        self.assertIsNone(template.functional_type)

    def test_template_tags_creation(self):
        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        template.tags.set([self.tag1, self.tag2])
        self.assertEqual(template.tags.count(), 2)
        self.assertIn(self.tag1, template.tags.all())
        self.assertIn(self.tag2, template.tags.all())

    def test_template_update_functional_type(self):
        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        template.update_if_has_perm(
            self.user, functional_type=PipelineFunctionalType.LOADING
        )
        template.refresh_from_db()
        self.assertEqual(template.functional_type, PipelineFunctionalType.LOADING)

    def test_template_update_tags(self):
        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
        )
        template.update_if_has_perm(self.user, tags=[self.tag1, self.tag2])
        template.refresh_from_db()
        self.assertEqual(template.tags.count(), 2)
        self.assertIn(self.tag1, template.tags.all())
        self.assertIn(self.tag2, template.tags.all())

    def test_pipeline_created_from_template_inherits_functional_type_and_tags(self):
        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test_code",
            workspace=self.workspace,
            source_pipeline=self.pipeline,
            functional_type=PipelineFunctionalType.COMPUTATION,
        )
        template.tags.set([self.tag1, self.tag2])

        pipeline_version = PipelineVersion.objects.create(
            pipeline=self.pipeline, version_number=1
        )
        template_version = template.create_version(pipeline_version, user=self.user)

        new_pipeline_version = template_version.create_pipeline_version(
            workspace=self.workspace, principal=self.user
        )
        new_pipeline = new_pipeline_version.pipeline

        self.assertEqual(
            new_pipeline.functional_type, PipelineFunctionalType.COMPUTATION
        )
        self.assertEqual(new_pipeline.tags.count(), 2)
        self.assertIn(self.tag1, new_pipeline.tags.all())
        self.assertIn(self.tag2, new_pipeline.tags.all())

    def test_template_created_from_pipeline_inherits_functional_type_and_tags(self):
        pipeline_with_metadata = Pipeline.objects.create(
            name="Pipeline with metadata",
            code="pipeline-with-metadata",
            workspace=self.workspace,
            functional_type=PipelineFunctionalType.LOADING,
        )
        pipeline_with_metadata.tags.set([self.tag1, self.tag2])

        template, created = pipeline_with_metadata.get_or_create_template(
            name="Template from pipeline",
            code="template-from-pipeline",
            description="Test template",
        )

        self.assertTrue(created)
        self.assertEqual(template.functional_type, PipelineFunctionalType.LOADING)
        self.assertEqual(template.tags.count(), 2)
        self.assertIn(self.tag1, template.tags.all())
        self.assertIn(self.tag2, template.tags.all())


class PipelineTemplatePublisherTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "user_template@bluesquarehub.com", "password", is_superuser=True
        )

        cls.BLUESQUARE_ORG = Organization.objects.create(
            name=PUBLISHER_BLUESQUARE,
            short_name="bluesquare",
            organization_type="CORPORATE",
        )

        cls.OTHER_ORG = Organization.objects.create(
            name="Other Organization",
            short_name="other-org",
            organization_type="CORPORATE",
        )

        cls.WORKSPACE_NO_ORG = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Workspace without org",
            description="Test workspace without organization",
        )

        cls.WORKSPACE_BLUESQUARE = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Workspace with Bluesquare org",
            description="Test workspace with Bluesquare organization",
            organization=cls.BLUESQUARE_ORG,
        )

        cls.WORKSPACE_OTHER_ORG = Workspace.objects.create_if_has_perm(
            cls.USER_ADMIN,
            name="Workspace with other org",
            description="Test workspace with other organization",
            organization=cls.OTHER_ORG,
        )

    def test_publisher_defaults_to_community_when_no_organization(self):
        pipeline = Pipeline.objects.create(
            name="Test Pipeline",
            code="test-pipeline-no-org",
            workspace=self.WORKSPACE_NO_ORG,
        )
        template, created = pipeline.get_or_create_template(
            name="Test Template",
            code="test-template-no-org",
            description="Test template without organization",
        )

        self.assertTrue(created)
        self.assertEqual(template.publisher, PUBLISHER_COMMUNITY)

    def test_publisher_is_bluesquare_when_organization_is_bluesquare(self):
        pipeline = Pipeline.objects.create(
            name="Test Pipeline Bluesquare",
            code="test-pipeline-bluesquare",
            workspace=self.WORKSPACE_BLUESQUARE,
        )
        template, created = pipeline.get_or_create_template(
            name="Test Template Bluesquare",
            code="test-template-bluesquare",
            description="Test template with Bluesquare organization",
        )

        self.assertTrue(created)
        self.assertEqual(template.publisher, PUBLISHER_BLUESQUARE)

    def test_publisher_defaults_to_community_when_other_organization(self):
        pipeline = Pipeline.objects.create(
            name="Test Pipeline Other Org",
            code="test-pipeline-other-org",
            workspace=self.WORKSPACE_OTHER_ORG,
        )
        template, created = pipeline.get_or_create_template(
            name="Test Template Other Org",
            code="test-template-other-org",
            description="Test template with other organization",
        )

        self.assertTrue(created)
        self.assertEqual(template.publisher, PUBLISHER_COMMUNITY)
