from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
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
        cls.PIPELINE = Pipeline.objects.create(
            name="Test Pipeline", code="Test Pipeline", workspace=cls.WS1
        )
        cls.PIPELINE_VERSION1 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            version_number=1,
            description="Initial version",
            parameters=[{"code": "param_1"}],
            config=[{"param_1": 1}],
            zipfile=str.encode("some_bytes"),
        )
        cls.PIPELINE_VERSION2 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE,
            version_number=2,
            description="Second version",
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

    def test_create_pipeline_from_template_version(self):
        self.client.force_login(self.USER_ROOT)
        self.create_template_version(self.PIPELINE_VERSION1.id, [{"versionNumber": 1}])
        r = self.run_query(
            """
                mutation createPipelineFromTemplateVersion($input: CreatePipelineFromTemplateVersionInput!) {
                    createPipelineFromTemplateVersion(input: $input) {
                        success errors pipeline {name code currentVersion {zipfile parameters {code default} config}}
                    }
                }
            """,
            {
                "input": {
                    "workspaceSlug": self.WS1.slug,
                    "pipelineTemplateVersionId": str(
                        self.PIPELINE_VERSION1.template_version.id
                    ),
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipeline": {
                    "name": self.PIPELINE.name,
                    "code": "Test Pipeline (from Template)",
                    "currentVersion": {
                        "zipfile": "c29tZV9ieXRlcw==",
                        "parameters": [{"code": "param_1", "default": None}],
                        "config": [{"param_1": 1}],
                    },
                },
            },
            r["data"]["createPipelineFromTemplateVersion"],
        )

        r = self.run_query(
            """
                mutation createPipelineFromTemplateVersion($input: CreatePipelineFromTemplateVersionInput!) {
                    createPipelineFromTemplateVersion(input: $input) {
                        success errors pipeline {name code currentVersion {zipfile parameters {code default} config}}
                    }
                }
            """,
            {
                "input": {
                    "workspaceSlug": self.WS1.slug,
                    "pipelineTemplateVersionId": str(
                        self.PIPELINE_VERSION1.template_version.id
                    ),
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PIPELINE_ALREADY_EXISTS"],
                "pipeline": None,
            },
            r["data"]["createPipelineFromTemplateVersion"],
        )
