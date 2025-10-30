from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipeline_templates.models import PipelineTemplate
from hexa.pipelines.models import Pipeline
from hexa.tags.models import Tag
from hexa.user_management.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
    User,
)
from hexa.workspaces.models import Workspace


class WorkspaceTagsTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_ADMIN = User.objects.create_user(
            "admin@test.com",
            "password",
            is_superuser=True,
        )

        cls.ORG1 = Organization.objects.create(name="Organization 1", short_name="org1")
        cls.ORG2 = Organization.objects.create(name="Organization 2", short_name="org2")

        OrganizationMembership.objects.create(
            organization=cls.ORG1,
            user=cls.USER_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )
        OrganizationMembership.objects.create(
            organization=cls.ORG2,
            user=cls.USER_ADMIN,
            role=OrganizationMembershipRole.ADMIN,
        )

        with (
            patch("hexa.workspaces.models.create_database"),
            patch("hexa.workspaces.models.load_database_sample_data"),
        ):
            cls.WS1_ORG1 = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN,
                name="Workspace 1 Org 1",
                description="First workspace in org 1",
                organization=cls.ORG1,
            )
            cls.WS2_ORG1 = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN,
                name="Workspace 2 Org 1",
                description="Second workspace in org 1",
                organization=cls.ORG1,
            )
            cls.WS1_ORG2 = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN,
                name="Workspace 1 Org 2",
                description="First workspace in org 2",
                organization=cls.ORG2,
            )
            cls.WS_STANDALONE = Workspace.objects.create_if_has_perm(
                cls.USER_ADMIN,
                name="Standalone Workspace",
                description="Workspace without organization",
                organization=None,
            )

    def test_workspace_pipeline_tags_scoped_to_workspace(self):
        """Verify pipelineTags only returns tags from pipelines in the specific workspace"""
        tag1 = Tag.objects.create(name="ml-tag")
        tag2 = Tag.objects.create(name="etl-tag")
        tag3 = Tag.objects.create(name="analytics-tag")

        pipeline1 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS1_ORG1,
            name="Pipeline in WS1",
        )
        pipeline1.tags.add(tag1, tag2)

        pipeline2 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS2_ORG1,
            name="Pipeline in WS2",
        )
        pipeline2.tags.add(tag3)

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query WorkspacePipelineTags($slug: String!) {
                workspace(slug: $slug) {
                    slug
                    pipelineTags
                }
            }
            """,
            {"slug": self.WS1_ORG1.slug},
        )

        ws1_tags = r["data"]["workspace"]["pipelineTags"]
        self.assertIn("ml-tag", ws1_tags)
        self.assertIn("etl-tag", ws1_tags)
        self.assertNotIn("analytics-tag", ws1_tags)

        r = self.run_query(
            """
            query WorkspacePipelineTags($slug: String!) {
                workspace(slug: $slug) {
                    slug
                    pipelineTags
                }
            }
            """,
            {"slug": self.WS2_ORG1.slug},
        )

        ws2_tags = r["data"]["workspace"]["pipelineTags"]
        self.assertNotIn("ml-tag", ws2_tags)
        self.assertNotIn("etl-tag", ws2_tags)
        self.assertIn("analytics-tag", ws2_tags)

    def test_workspace_pipeline_template_tags_scoped_to_organization(self):
        """Verify pipelineTemplateTags returns tags from all workspaces in the organization"""
        tag1 = Tag.objects.create(name="template-ml")
        tag2 = Tag.objects.create(name="template-etl")
        tag3 = Tag.objects.create(name="template-viz")

        pipeline1 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS1_ORG1,
            name="Source Pipeline WS1",
        )
        template1 = PipelineTemplate.objects.create(
            workspace=self.WS1_ORG1,
            name="Template in WS1",
            code="template-ws1",
            source_pipeline=pipeline1,
        )
        template1.tags.add(tag1, tag2)

        pipeline2 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS2_ORG1,
            name="Source Pipeline WS2",
        )
        template2 = PipelineTemplate.objects.create(
            workspace=self.WS2_ORG1,
            name="Template in WS2",
            code="template-ws2",
            source_pipeline=pipeline2,
        )
        template2.tags.add(tag3)

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query WorkspaceTemplateTags($slug: String!) {
                workspace(slug: $slug) {
                    slug
                    pipelineTemplateTags
                }
            }
            """,
            {"slug": self.WS1_ORG1.slug},
        )

        ws1_template_tags = r["data"]["workspace"]["pipelineTemplateTags"]
        self.assertIn("template-ml", ws1_template_tags)
        self.assertIn("template-etl", ws1_template_tags)
        self.assertIn("template-viz", ws1_template_tags)

        r = self.run_query(
            """
            query WorkspaceTemplateTags($slug: String!) {
                workspace(slug: $slug) {
                    slug
                    pipelineTemplateTags
                }
            }
            """,
            {"slug": self.WS2_ORG1.slug},
        )

        ws2_template_tags = r["data"]["workspace"]["pipelineTemplateTags"]
        self.assertIn("template-ml", ws2_template_tags)
        self.assertIn("template-etl", ws2_template_tags)
        self.assertIn("template-viz", ws2_template_tags)

    def test_workspace_pipeline_template_tags_isolated_by_organization(self):
        """Verify pipelineTemplateTags doesn't include tags from other organizations"""
        tag_org1 = Tag.objects.create(name="org1-template")
        tag_org2 = Tag.objects.create(name="org2-template")

        pipeline_org1 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS1_ORG1,
            name="Source Pipeline Org1",
        )
        template_org1 = PipelineTemplate.objects.create(
            workspace=self.WS1_ORG1,
            name="Template in Org 1",
            code="template-org1",
            source_pipeline=pipeline_org1,
        )
        template_org1.tags.add(tag_org1)

        pipeline_org2 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS1_ORG2,
            name="Source Pipeline Org2",
        )
        template_org2 = PipelineTemplate.objects.create(
            workspace=self.WS1_ORG2,
            name="Template in Org 2",
            code="template-org2",
            source_pipeline=pipeline_org2,
        )
        template_org2.tags.add(tag_org2)

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query WorkspaceTemplateTags($slug: String!) {
                workspace(slug: $slug) {
                    slug
                    pipelineTemplateTags
                }
            }
            """,
            {"slug": self.WS1_ORG1.slug},
        )

        org1_tags = r["data"]["workspace"]["pipelineTemplateTags"]
        self.assertIn("org1-template", org1_tags)
        self.assertNotIn("org2-template", org1_tags)

        r = self.run_query(
            """
            query WorkspaceTemplateTags($slug: String!) {
                workspace(slug: $slug) {
                    slug
                    pipelineTemplateTags
                }
            }
            """,
            {"slug": self.WS1_ORG2.slug},
        )

        org2_tags = r["data"]["workspace"]["pipelineTemplateTags"]
        self.assertNotIn("org1-template", org2_tags)
        self.assertIn("org2-template", org2_tags)

    def test_filter_pipelines_by_tags_respects_workspace_scope(self):
        """Verify pipeline query filters tags by workspace when workspace_slug provided"""
        shared_tag = Tag.objects.create(name="shared-pipeline-tag")

        pipeline_ws1 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS1_ORG1,
            name="Pipeline in WS1 with shared tag",
        )
        pipeline_ws1.tags.add(shared_tag)

        pipeline_ws2 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS2_ORG1,
            name="Pipeline in WS2 with shared tag",
        )
        pipeline_ws2.tags.add(shared_tag)

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query FilterPipelines($workspaceSlug: String!, $tags: [String!]) {
                pipelines(workspaceSlug: $workspaceSlug, tags: $tags) {
                    items {
                        id
                        name
                        workspace {
                            slug
                        }
                    }
                }
            }
            """,
            {"workspaceSlug": self.WS1_ORG1.slug, "tags": ["shared-pipeline-tag"]},
        )

        pipelines = r["data"]["pipelines"]["items"]
        self.assertEqual(len(pipelines), 1)
        self.assertEqual(pipelines[0]["name"], "Pipeline in WS1 with shared tag")
        self.assertEqual(pipelines[0]["workspace"]["slug"], self.WS1_ORG1.slug)

        r = self.run_query(
            """
            query FilterPipelines($workspaceSlug: String!, $tags: [String!]) {
                pipelines(workspaceSlug: $workspaceSlug, tags: $tags) {
                    items {
                        id
                        name
                        workspace {
                            slug
                        }
                    }
                }
            }
            """,
            {"workspaceSlug": self.WS2_ORG1.slug, "tags": ["shared-pipeline-tag"]},
        )

        pipelines = r["data"]["pipelines"]["items"]
        self.assertEqual(len(pipelines), 1)
        self.assertEqual(pipelines[0]["name"], "Pipeline in WS2 with shared tag")
        self.assertEqual(pipelines[0]["workspace"]["slug"], self.WS2_ORG1.slug)

    def test_filter_templates_by_tags_respects_organization_scope(self):
        """Verify template query filters tags by organization when workspace_slug provided"""
        shared_tag = Tag.objects.create(name="shared-template-tag")

        pipeline_ws1 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS1_ORG1,
            name="Source for Template WS1",
        )
        template_ws1 = PipelineTemplate.objects.create(
            workspace=self.WS1_ORG1,
            name="Template in WS1",
            code="template-ws1-shared",
            source_pipeline=pipeline_ws1,
        )
        template_ws1.tags.add(shared_tag)

        pipeline_ws2 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS2_ORG1,
            name="Source for Template WS2",
        )
        template_ws2 = PipelineTemplate.objects.create(
            workspace=self.WS2_ORG1,
            name="Template in WS2",
            code="template-ws2-shared",
            source_pipeline=pipeline_ws2,
        )
        template_ws2.tags.add(shared_tag)

        pipeline_org2 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS1_ORG2,
            name="Source for Template Org2",
        )
        template_org2 = PipelineTemplate.objects.create(
            workspace=self.WS1_ORG2,
            name="Template in Org 2",
            code="template-org2-shared",
            source_pipeline=pipeline_org2,
        )
        template_org2.tags.add(shared_tag)

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query FilterTemplates($workspaceSlug: String, $tags: [String!]) {
                pipelineTemplates(workspaceSlug: $workspaceSlug, tags: $tags) {
                    items {
                        id
                        name
                        workspace {
                            slug
                            organization {
                                name
                            }
                        }
                    }
                }
            }
            """,
            {"workspaceSlug": self.WS1_ORG1.slug, "tags": ["shared-template-tag"]},
        )

        templates = r["data"]["pipelineTemplates"]["items"]
        self.assertEqual(len(templates), 2)
        template_names = [t["name"] for t in templates]
        self.assertIn("Template in WS1", template_names)
        self.assertIn("Template in WS2", template_names)
        self.assertNotIn("Template in Org 2", template_names)

        for template in templates:
            self.assertEqual(
                template["workspace"]["organization"]["name"], "Organization 1"
            )

    def test_workspace_pipeline_template_tags_without_organization(self):
        """Verify pipelineTemplateTags is workspace-scoped when workspace has no organization"""
        tag_standalone = Tag.objects.create(name="standalone-template")
        tag_org1 = Tag.objects.create(name="org1-only-template")

        pipeline_standalone = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS_STANDALONE,
            name="Source for Standalone Template",
        )
        template_standalone = PipelineTemplate.objects.create(
            workspace=self.WS_STANDALONE,
            name="Template in Standalone",
            code="template-standalone",
            source_pipeline=pipeline_standalone,
        )
        template_standalone.tags.add(tag_standalone)

        pipeline_org1 = Pipeline.objects.create_if_has_perm(
            principal=self.USER_ADMIN,
            workspace=self.WS1_ORG1,
            name="Source for Org1 Template",
        )
        template_org1 = PipelineTemplate.objects.create(
            workspace=self.WS1_ORG1,
            name="Template in Org 1",
            code="template-org1-only",
            source_pipeline=pipeline_org1,
        )
        template_org1.tags.add(tag_org1)

        self.client.force_login(self.USER_ADMIN)
        r = self.run_query(
            """
            query WorkspaceTemplateTags($slug: String!) {
                workspace(slug: $slug) {
                    slug
                    organization {
                        name
                    }
                    pipelineTemplateTags
                }
            }
            """,
            {"slug": self.WS_STANDALONE.slug},
        )

        standalone_tags = r["data"]["workspace"]["pipelineTemplateTags"]
        self.assertIsNone(r["data"]["workspace"]["organization"])
        self.assertIn("standalone-template", standalone_tags)
        self.assertNotIn("org1-only-template", standalone_tags)
