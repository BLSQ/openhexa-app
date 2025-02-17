from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
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
    PIPELINE1 = None
    PIPELINE2 = None
    PIPELINE3 = None
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
            cls.WS2 = Workspace.objects.create_if_has_perm(
                cls.USER_ROOT,
                name="WS2",
                description="Workspace 2",
            )
        cls.PIPELINE1 = Pipeline.objects.create(
            name="Test Pipeline", code="Test Pipeline", workspace=cls.WS1
        )
        cls.PIPELINE_VERSION1 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE1,
            version_number=1,
            description="Initial version",
            parameters=[{"code": "param_1", "default": 23}],
            config={"param_1": 1},
            zipfile=str.encode("some_bytes"),
        )
        cls.PIPELINE_VERSION2 = PipelineVersion.objects.create(
            pipeline=cls.PIPELINE1,
            version_number=2,
            description="Second version",
        )
        cls.PIPELINE2 = Pipeline.objects.create(
            name="Pipeline 2", code="pipeline-2", workspace=cls.WS1
        )
        cls.PIPELINE3 = Pipeline.objects.create(
            name="Pipeline 3", code="pipeline-3", workspace=cls.WS1
        )

    def create_template_version(self, pipeline_version_id, expected_versions):
        r = self.run_query(
            """
                mutation createPipelineTemplateVersion($input: CreatePipelineTemplateVersionInput!) {
                    createPipelineTemplateVersion(input: $input) {
                        success errors pipelineTemplate {name code versions(page:1, perPage:10) { items { versionNumber }}}
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
                    "pipelineId": str(self.PIPELINE1.id),
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
                    "versions": {"items": expected_versions},
                },
            },
            r["data"]["createPipelineTemplateVersion"],
        )

    def test_create_template_version(self):
        self.client.force_login(self.USER_ROOT)
        self.create_template_version(self.PIPELINE_VERSION1.id, [{"versionNumber": 1}])
        self.create_template_version(
            self.PIPELINE_VERSION2.id, [{"versionNumber": 2}, {"versionNumber": 1}]
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
                    "workspaceSlug": self.WS2.slug,
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
                    "name": self.PIPELINE1.name,
                    "code": "test-pipeline",
                    "currentVersion": {
                        "zipfile": "c29tZV9ieXRlcw==",
                        "parameters": [{"code": "param_1", "default": 23}],
                        "config": {},
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
                    "workspaceSlug": self.WS2.slug,
                    "pipelineTemplateVersionId": str(
                        self.PIPELINE_VERSION1.template_version.id
                    ),
                }
            },
        )
        self.assertIn(
            "test-pipeline-",
            r["data"]["createPipelineFromTemplateVersion"]["pipeline"]["code"],
        )

    def test_get_pipeline_templates(self):
        self.client.force_login(self.USER_ROOT)
        PipelineTemplate.objects.create(
            name="Template 1", code="Code 1", source_pipeline=self.PIPELINE1
        )
        PipelineTemplate.objects.create(
            name="Template 2", code="Code 2", source_pipeline=self.PIPELINE2
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

    def test_searching_pipeline_templates(self):
        self.client.force_login(self.USER_ROOT)
        PipelineTemplate.objects.create(
            name="Template 1", code="Code 1", source_pipeline=self.PIPELINE1
        )
        PipelineTemplate.objects.create(
            name="Template 2", code="Code 2", source_pipeline=self.PIPELINE2
        )
        PipelineTemplate.objects.create(
            name="Template 22", code="Code 22", source_pipeline=self.PIPELINE3
        )
        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 1, search: "Template 3") {
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
                "totalPages": 1,
                "totalItems": 0,
                "items": [],
            },
            r["data"]["pipelineTemplates"],
        )
        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 2, search: "Template 2") {
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
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"code": "Code 2", "name": "Template 2"},
                    {"code": "Code 22", "name": "Template 22"},
                ],
            },
            r["data"]["pipelineTemplates"],
        )

    def test_delete_pipeline_template(self):
        self.client.force_login(self.USER_ROOT)

        pipeline_template = PipelineTemplate.objects.create(
            name="Template to Delete",
            code="template_to_delete",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        PipelineTemplateVersion.objects.create(
            template=pipeline_template,
            version_number=1,
            source_pipeline_version=self.PIPELINE_VERSION1,
        )

        response = self.run_query(
            """
            mutation deletePipelineTemplate($input: DeletePipelineTemplateInput!) {
                deletePipelineTemplate(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(pipeline_template.id),
                }
            },
        )

        self.assertEqual(response["data"]["deletePipelineTemplate"]["success"], True)
        self.assertEqual(response["data"]["deletePipelineTemplate"]["errors"], [])

        self.PIPELINE1.refresh_from_db()
        self.assertTrue(self.PIPELINE1.template.is_deleted)
        self.assertFalse(
            PipelineTemplate.objects.filter(id=pipeline_template.id).exists()
        )
