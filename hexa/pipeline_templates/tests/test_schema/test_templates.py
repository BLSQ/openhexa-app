from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipeline_templates.models import PipelineTemplate
from hexa.pipelines.models import (
    Pipeline,
    PipelineVersion,
)
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
)


class PipelineTemplatesTest(GraphQLTestCase):
    USER_ROOT = None
    PIPELINE = None
    PIPELINE_VERSION1 = None
    PIPELINE_VERSION2 = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            cls.WS1 = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS1",
                description="Workspace 1",
            )
        cls.PIPELINE = Pipeline.objects.create(name="Test Pipeline", workspace=cls.WS1)
        cls.PIPELINE_VERSION1 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            version_number=1,
            description="Initial version",
        )
        cls.PIPELINE_VERSION2 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            version_number=2,
            description="Second version",
        )
        cls.OTHER_PIPELINE = Pipeline.objects.create(
            name="Other Pipeline", code="other-pipeline", workspace=cls.WS1
        )

    def create_template_version(self, pipeline_version_id, expected_versions):
        r = self.run_query(
            """
                mutation createPipelineTemplateVersion($input: CreatePipelineTemplateVersionInput!) {
                    createPipelineTemplateVersion(input: $input) {
                        success errors pipelineTemplate {name code versions {versionNumber}}
                    }
                }
            """,
            {
                "input": {
                    "name": "Template1",
                    "code": "template_code",
                    "description": "A test template",
                    "config": "{}",
                    "workspaceSlug": self.WS1.slug,
                    "pipelineId": str(self.PIPELINE.id),
                    "pipelineVersionId": str(pipeline_version_id),
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipelineTemplate": {
                    "name": "Template1",
                    "code": "template_code",
                    "versions": expected_versions,
                },
            },
            r["data"]["createPipelineTemplateVersion"],
        )

    def test_create_template_version(self):
        self.client.force_login(self.USER_ROOT)
        self.create_template_version(self.PIPELINE_VERSION1.id, [{"versionNumber": 1}])
        self.create_template_version(
            self.PIPELINE_VERSION2.id, [{"versionNumber": 1}, {"versionNumber": 2}]
        )

    def test_get_pipeline_templates(self):
        PipelineTemplate.objects.create(
            name="Template 1", code="Code 1", source_pipeline=self.PIPELINE
        )
        PipelineTemplate.objects.create(
            name="Template 2", code="Code 2", source_pipeline=self.OTHER_PIPELINE
        )
        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 1) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                        name
                        code
                    }
                }
            }
            """
        )
        self.assertEqual(
            {
                "pageNumber": 1,
                "totalPages": 2,
                "totalItems": 2,
                "items": [{"code": "Code 1", "name": "Template 1"}],
            },
            r["data"]["pipelineTemplates"],
        )
