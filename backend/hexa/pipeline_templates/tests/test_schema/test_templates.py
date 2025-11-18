from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.pipelines.models import (
    Pipeline,
    PipelineVersion,
)
from hexa.user_management.models import Organization, User
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
            name="Template 1",
            code="Code 1",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        PipelineTemplate.objects.create(
            name="Template 2",
            code="Code 2",
            source_pipeline=self.PIPELINE2,
            workspace=self.WS1,
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
            name="Template 1",
            code="Code 1",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        PipelineTemplate.objects.create(
            name="Template 2",
            code="Code 2",
            source_pipeline=self.PIPELINE2,
            workspace=self.WS1,
        )
        PipelineTemplate.objects.create(
            name="Template 22",
            code="Code 22",
            source_pipeline=self.PIPELINE3,
            workspace=self.WS1,
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

    def test_update_pipeline_template_with_tags(self):
        self.client.force_login(self.USER_ROOT)

        pipeline_template = PipelineTemplate.objects.create(
            name="Template with Tags",
            code="template_with_tags",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )

        response = self.run_query(
            """
            mutation updatePipelineTemplate($input: UpdateTemplateInput!) {
                updatePipelineTemplate(input: $input) {
                    success
                    errors
                    template {
                        id
                        name
                        tags {
                            id
                            name
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(pipeline_template.id),
                    "tags": ["new-tag", "another-tag"],
                }
            },
        )

        self.assertEqual(response["data"]["updatePipelineTemplate"]["success"], True)
        self.assertEqual(response["data"]["updatePipelineTemplate"]["errors"], [])

        template_data = response["data"]["updatePipelineTemplate"]["template"]
        self.assertEqual(len(template_data["tags"]), 2)
        tag_names = {tag["name"] for tag in template_data["tags"]}
        self.assertEqual(tag_names, {"new-tag", "another-tag"})

        pipeline_template.refresh_from_db()
        self.assertEqual(pipeline_template.tags.count(), 2)

    def test_update_pipeline_template_with_invalid_tags(self):
        self.client.force_login(self.USER_ROOT)

        pipeline_template = PipelineTemplate.objects.create(
            name="Template for Invalid Tags Test",
            code="template_invalid_tags",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )

        response = self.run_query(
            """
            mutation updatePipelineTemplate($input: UpdateTemplateInput!) {
                updatePipelineTemplate(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "id": str(pipeline_template.id),
                    "tags": ["valid-tag", ""],
                }
            },
        )

        self.assertEqual(response["data"]["updatePipelineTemplate"]["success"], False)
        self.assertEqual(
            response["data"]["updatePipelineTemplate"]["errors"], ["INVALID_CONFIG"]
        )

    def test_search_pipeline_templates_by_tags_and_functional_type(self):
        from hexa.pipelines.models import PipelineFunctionalType
        from hexa.tags.models import Tag

        self.client.force_login(self.USER_ROOT)

        tag1 = Tag.objects.create(name="data-ingestion")
        tag2 = Tag.objects.create(name="analytics")
        tag3 = Tag.objects.create(name="reporting")

        template1 = PipelineTemplate.objects.create(
            name="ETL Template",
            code="etl-template",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
            functional_type=PipelineFunctionalType.EXTRACTION,
        )
        template1.tags.add(tag1)

        template2 = PipelineTemplate.objects.create(
            name="Analytics Template",
            code="analytics-template",
            source_pipeline=self.PIPELINE2,
            workspace=self.WS1,
            functional_type=PipelineFunctionalType.COMPUTATION,
        )
        template2.tags.add(tag2)

        template3 = PipelineTemplate.objects.create(
            name="Report Generator",
            code="report-generator",
            source_pipeline=self.PIPELINE3,
            workspace=self.WS1,
            functional_type=PipelineFunctionalType.TRANSFORMATION,
        )
        template3.tags.add(tag3)

        response = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, search: "ingestion") {
                    totalItems
                    items {
                        name
                        code
                    }
                }
            }
            """
        )
        self.assertEqual(response["data"]["pipelineTemplates"]["totalItems"], 1)
        self.assertEqual(
            response["data"]["pipelineTemplates"]["items"][0]["code"], "etl-template"
        )

        response = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, search: "EXTRACTION") {
                    totalItems
                    items {
                        name
                        code
                    }
                }
            }
            """
        )
        self.assertEqual(response["data"]["pipelineTemplates"]["totalItems"], 1)
        self.assertEqual(
            response["data"]["pipelineTemplates"]["items"][0]["code"], "etl-template"
        )

        response = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, search: "analytics") {
                    totalItems
                    items {
                        name
                        code
                    }
                }
            }
            """
        )
        self.assertEqual(response["data"]["pipelineTemplates"]["totalItems"], 1)
        self.assertEqual(
            response["data"]["pipelineTemplates"]["items"][0]["code"],
            "analytics-template",
        )

        response = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, search: "transformation") {
                    totalItems
                    items {
                        name
                        code
                    }
                }
            }
            """
        )
        self.assertEqual(response["data"]["pipelineTemplates"]["totalItems"], 1)
        self.assertEqual(
            response["data"]["pipelineTemplates"]["items"][0]["code"],
            "report-generator",
        )

    def test_templates_are_organization_wide_not_workspace_specific(self):
        """Test that pipeline templates are visible across all workspaces in an organization."""
        self.client.force_login(self.USER_ROOT)

        org = Organization.objects.create(name="Test Org")

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            ws_org_1 = Workspace.objects.create_if_has_perm(
                self.USER_ROOT,
                name="Org WS 1",
                description="First workspace in org",
                organization=org,
            )
            ws_org_2 = Workspace.objects.create_if_has_perm(
                self.USER_ROOT,
                name="Org WS 2",
                description="Second workspace in org",
                organization=org,
            )

        pipeline_in_ws1 = Pipeline.objects.create(
            name="Pipeline in WS1", code="pipeline-ws1", workspace=ws_org_1
        )
        pipeline_in_ws2 = Pipeline.objects.create(
            name="Pipeline in WS2", code="pipeline-ws2", workspace=ws_org_2
        )

        PipelineTemplate.objects.create(
            name="Template from WS1",
            code="template-ws1",
            source_pipeline=pipeline_in_ws1,
            workspace=ws_org_1,
        )
        PipelineTemplate.objects.create(
            name="Template from WS2",
            code="template-ws2",
            source_pipeline=pipeline_in_ws2,
            workspace=ws_org_2,
        )

        response = self.run_query(
            """
            query pipelineTemplates($workspaceSlug: String) {
                pipelineTemplates(page: 1, perPage: 10, workspaceSlug: $workspaceSlug) {
                    totalItems
                    items {
                        name
                        code
                    }
                }
            }
            """
        )

        self.assertEqual(response["data"]["pipelineTemplates"]["totalItems"], 2)
        template_codes = {
            item["code"] for item in response["data"]["pipelineTemplates"]["items"]
        }
        self.assertEqual(template_codes, {"template-ws1", "template-ws2"})

        response = self.run_query(
            """
            query pipelineTemplates($workspaceSlug: String) {
                pipelineTemplates(page: 1, perPage: 10, workspaceSlug: $workspaceSlug) {
                    totalItems
                    items {
                        name
                        code
                    }
                }
            }
            """
        )

        self.assertEqual(response["data"]["pipelineTemplates"]["totalItems"], 2)
        template_codes = {
            item["code"] for item in response["data"]["pipelineTemplates"]["items"]
        }
        self.assertEqual(template_codes, {"template-ws1", "template-ws2"})

    def test_get_pipeline_template_version(self):
        self.client.force_login(self.USER_ROOT)

        pipeline_template = PipelineTemplate.objects.create(
            name="Template 1",
            code="template-1",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        version = PipelineTemplateVersion.objects.create(
            template=pipeline_template,
            version_number=1,
            source_pipeline_version=self.PIPELINE_VERSION1,
        )

        r = self.run_query(
            """
            query getPipelineTemplateVersion($id: UUID!) {
                pipelineTemplateVersion(id: $id) {
                    id
                    versionNumber
                    template {
                        code
                    }
                }
            }
            """,
            {"id": str(version.id)},
        )

        self.assertEqual(r["data"]["pipelineTemplateVersion"]["id"], str(version.id))
        self.assertEqual(r["data"]["pipelineTemplateVersion"]["versionNumber"], 1)
        self.assertEqual(
            r["data"]["pipelineTemplateVersion"]["template"]["code"], "template-1"
        )

    def test_get_pipeline_template_version_not_found(self):
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            query getPipelineTemplateVersion($id: UUID!) {
                pipelineTemplateVersion(id: $id) {
                    id
                }
            }
            """,
            {"id": "00000000-0000-0000-0000-000000000000"},
        )

        self.assertIsNone(r["data"]["pipelineTemplateVersion"])

    def test_get_pipeline_template_version_permission_denied(self):
        user_no_access = User.objects.create_user(
            "noaccess@bluesquarehub.com", "standardpassword"
        )
        self.client.force_login(user_no_access)

        pipeline_template = PipelineTemplate.objects.create(
            name="Template 1",
            code="template-1",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        version = PipelineTemplateVersion.objects.create(
            template=pipeline_template,
            version_number=1,
            source_pipeline_version=self.PIPELINE_VERSION1,
        )

        r = self.run_query(
            """
            query getPipelineTemplateVersion($id: UUID!) {
                pipelineTemplateVersion(id: $id) {
                    id
                }
            }
            """,
            {"id": str(version.id)},
        )

        self.assertIsNone(r["data"]["pipelineTemplateVersion"])

    def test_pipelines_count_field_with_fallback(self):
        self.client.force_login(self.USER_ROOT)

        template = PipelineTemplate.objects.create(
            name="Template for Count Test",
            code="template-count-test",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )

        Pipeline.objects.create(
            name="Pipeline 1 from Template",
            code="pipeline-1-from-template",
            workspace=self.WS1,
            source_template=template,
        )
        Pipeline.objects.create(
            name="Pipeline 2 from Template",
            code="pipeline-2-from-template",
            workspace=self.WS1,
            source_template=template,
        )
        pipeline3 = Pipeline.objects.create(
            name="Pipeline 3 from Template (Deleted)",
            code="pipeline-3-from-template",
            workspace=self.WS1,
            source_template=template,
        )
        pipeline3.delete()

        r = self.run_query(
            """
            query getTemplateByCode($code: String!) {
                templateByCode(code: $code) {
                    code
                    name
                    pipelinesCount
                }
            }
            """,
            {"code": "template-count-test"},
        )

        self.assertEqual(r["data"]["templateByCode"]["code"], "template-count-test")
        self.assertEqual(r["data"]["templateByCode"]["pipelinesCount"], 2)

    def test_pipeline_templates_default_sorting_by_popularity(self):
        self.client.force_login(self.USER_ROOT)

        PipelineTemplate.objects.create(
            name="Alpha Template",
            code="alpha-template",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        template_beta = PipelineTemplate.objects.create(
            name="Beta Template",
            code="beta-template",
            source_pipeline=self.PIPELINE2,
            workspace=self.WS1,
        )
        template_gamma = PipelineTemplate.objects.create(
            name="Gamma Template",
            code="gamma-template",
            source_pipeline=self.PIPELINE3,
            workspace=self.WS1,
        )

        Pipeline.objects.create(
            name="Pipeline from Beta 1",
            code="pipeline-beta-1",
            workspace=self.WS1,
            source_template=template_beta,
        )
        Pipeline.objects.create(
            name="Pipeline from Beta 2",
            code="pipeline-beta-2",
            workspace=self.WS1,
            source_template=template_beta,
        )
        Pipeline.objects.create(
            name="Pipeline from Beta 3",
            code="pipeline-beta-3",
            workspace=self.WS1,
            source_template=template_beta,
        )

        Pipeline.objects.create(
            name="Pipeline from Gamma 1",
            code="pipeline-gamma-1",
            workspace=self.WS1,
            source_template=template_gamma,
        )

        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10) {
                    totalItems
                    items {
                        code
                        pipelinesCount
                    }
                }
            }
            """
        )

        self.assertEqual(r["data"]["pipelineTemplates"]["totalItems"], 3)
        items = r["data"]["pipelineTemplates"]["items"]
        self.assertEqual(items[0]["code"], "beta-template")
        self.assertEqual(items[0]["pipelinesCount"], 3)
        self.assertEqual(items[1]["code"], "gamma-template")
        self.assertEqual(items[1]["pipelinesCount"], 1)
        self.assertEqual(items[2]["code"], "alpha-template")
        self.assertEqual(items[2]["pipelinesCount"], 0)

    def test_pipeline_templates_sorting_by_name(self):
        self.client.force_login(self.USER_ROOT)

        PipelineTemplate.objects.create(
            name="Zebra Template",
            code="zebra-template",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        PipelineTemplate.objects.create(
            name="Alpha Template",
            code="alpha-template",
            source_pipeline=self.PIPELINE2,
            workspace=self.WS1,
        )
        PipelineTemplate.objects.create(
            name="Beta Template",
            code="beta-template",
            source_pipeline=self.PIPELINE3,
            workspace=self.WS1,
        )

        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, orderBy: NAME_ASC) {
                    items {
                        code
                        name
                    }
                }
            }
            """
        )
        items = r["data"]["pipelineTemplates"]["items"]
        self.assertEqual(items[0]["code"], "alpha-template")
        self.assertEqual(items[1]["code"], "beta-template")
        self.assertEqual(items[2]["code"], "zebra-template")

        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, orderBy: NAME_DESC) {
                    items {
                        code
                        name
                    }
                }
            }
            """
        )
        items = r["data"]["pipelineTemplates"]["items"]
        self.assertEqual(items[0]["code"], "zebra-template")
        self.assertEqual(items[1]["code"], "beta-template")
        self.assertEqual(items[2]["code"], "alpha-template")

    def test_pipeline_templates_sorting_by_created_at(self):
        from datetime import timedelta

        from django.utils import timezone

        self.client.force_login(self.USER_ROOT)

        now = timezone.now()

        template_old = PipelineTemplate.objects.create(
            name="Old Template",
            code="old-template",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        template_old.created_at = now - timedelta(days=10)
        template_old.save()

        template_new = PipelineTemplate.objects.create(
            name="New Template",
            code="new-template",
            source_pipeline=self.PIPELINE2,
            workspace=self.WS1,
        )
        template_new.created_at = now - timedelta(days=1)
        template_new.save()

        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, orderBy: CREATED_AT_ASC) {
                    items {
                        code
                    }
                }
            }
            """
        )
        items = r["data"]["pipelineTemplates"]["items"]
        self.assertEqual(items[0]["code"], "old-template")
        self.assertEqual(items[1]["code"], "new-template")

        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, orderBy: CREATED_AT_DESC) {
                    items {
                        code
                    }
                }
            }
            """
        )
        items = r["data"]["pipelineTemplates"]["items"]
        self.assertEqual(items[0]["code"], "new-template")
        self.assertEqual(items[1]["code"], "old-template")

    def test_pipeline_templates_sorting_by_pipelines_count(self):
        self.client.force_login(self.USER_ROOT)

        template_many = PipelineTemplate.objects.create(
            name="Popular Template",
            code="popular-template",
            source_pipeline=self.PIPELINE1,
            workspace=self.WS1,
        )
        template_few = PipelineTemplate.objects.create(
            name="Less Popular Template",
            code="less-popular-template",
            source_pipeline=self.PIPELINE2,
            workspace=self.WS1,
        )

        for i in range(5):
            Pipeline.objects.create(
                name=f"Pipeline from Popular {i}",
                code=f"pipeline-popular-{i}",
                workspace=self.WS1,
                source_template=template_many,
            )

        Pipeline.objects.create(
            name="Pipeline from Less Popular",
            code="pipeline-less-popular",
            workspace=self.WS1,
            source_template=template_few,
        )

        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, orderBy: PIPELINES_COUNT_ASC) {
                    items {
                        code
                        pipelinesCount
                    }
                }
            }
            """
        )
        items = r["data"]["pipelineTemplates"]["items"]
        self.assertEqual(items[0]["code"], "less-popular-template")
        self.assertEqual(items[0]["pipelinesCount"], 1)
        self.assertEqual(items[1]["code"], "popular-template")
        self.assertEqual(items[1]["pipelinesCount"], 5)

        r = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10, orderBy: PIPELINES_COUNT_DESC) {
                    items {
                        code
                        pipelinesCount
                    }
                }
            }
            """
        )
        items = r["data"]["pipelineTemplates"]["items"]
        self.assertEqual(items[0]["code"], "popular-template")
        self.assertEqual(items[0]["pipelinesCount"], 5)
        self.assertEqual(items[1]["code"], "less-popular-template")
        self.assertEqual(items[1]["pipelinesCount"], 1)

    def test_template_publisher_field_returns_organization_name(self):
        self.client.force_login(self.USER_ROOT)

        org = Organization.objects.create(
            name="Test Organization",
            short_name="TEST",
            organization_type="CORPORATE",
        )

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            ws = Workspace.objects.create_if_has_perm(
                self.USER_ROOT,
                name="Test Workspace",
                description="Workspace under Test org",
                organization=org,
            )

        pipeline = Pipeline.objects.create(
            name="Test Pipeline",
            code="test-pipeline",
            workspace=ws,
        )

        template = PipelineTemplate.objects.create(
            name="Test Template",
            code="test-template",
            source_pipeline=pipeline,
            workspace=ws,
        )

        response = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10) {
                    items {
                        id
                        name
                        publisher
                    }
                }
            }
            """
        )

        items = response["data"]["pipelineTemplates"]["items"]
        template_item = next(
            (item for item in items if item["id"] == str(template.id)), None
        )
        self.assertIsNotNone(template_item)
        self.assertEqual(template_item["publisher"], "Test Organization")

    def test_template_filter_by_publisher(self):
        self.client.force_login(self.USER_ROOT)

        org1 = Organization.objects.create(
            name="Organization Alpha",
            short_name="ALPHA",
            organization_type="CORPORATE",
        )
        org2 = Organization.objects.create(
            name="Organization Beta",
            short_name="BETA",
            organization_type="CORPORATE",
        )

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            ws1 = Workspace.objects.create_if_has_perm(
                self.USER_ROOT,
                name="Alpha Workspace",
                description="Workspace under Alpha org",
                organization=org1,
            )
            ws2 = Workspace.objects.create_if_has_perm(
                self.USER_ROOT,
                name="Beta Workspace",
                description="Workspace under Beta org",
                organization=org2,
            )

        pipeline1 = Pipeline.objects.create(
            name="Alpha Pipeline",
            code="alpha-pipeline",
            workspace=ws1,
        )
        pipeline2 = Pipeline.objects.create(
            name="Beta Pipeline",
            code="beta-pipeline",
            workspace=ws2,
        )

        PipelineTemplate.objects.create(
            name="Alpha Template",
            code="alpha-template",
            source_pipeline=pipeline1,
            workspace=ws1,
        )
        PipelineTemplate.objects.create(
            name="Beta Template",
            code="beta-template",
            source_pipeline=pipeline2,
            workspace=ws2,
        )

        response = self.run_query(
            """
            query($publisher: String) {
                pipelineTemplates(page: 1, perPage: 10, publisher: $publisher) {
                    items {
                        id
                        name
                        publisher
                    }
                }
            }
            """,
            {"publisher": "Organization Alpha"},
        )

        items = response["data"]["pipelineTemplates"]["items"]
        alpha_items = [
            item for item in items if item["publisher"] == "Organization Alpha"
        ]
        beta_items = [
            item for item in items if item["publisher"] == "Organization Beta"
        ]

        self.assertGreaterEqual(len(alpha_items), 1)
        self.assertEqual(len(beta_items), 0)

    def test_template_filter_by_validation_status(self):
        self.client.force_login(self.USER_ROOT)

        org = Organization.objects.create(
            name="Test Organization",
            short_name="TEST",
            organization_type="CORPORATE",
        )

        with patch("hexa.workspaces.models.create_database"), patch(
            "hexa.workspaces.models.load_database_sample_data"
        ):
            ws = Workspace.objects.create_if_has_perm(
                self.USER_ROOT,
                name="Test Workspace",
                description="Test workspace",
                organization=org,
            )

        pipeline1 = Pipeline.objects.create(
            name="Validated Pipeline",
            code="validated-pipeline",
            workspace=ws,
        )
        pipeline2 = Pipeline.objects.create(
            name="Community Pipeline",
            code="community-pipeline",
            workspace=ws,
        )

        from django.utils import timezone

        validated_template = PipelineTemplate.objects.create(
            name="Validated Template",
            code="validated-template",
            source_pipeline=pipeline1,
            workspace=ws,
            validated_at=timezone.now(),
        )
        community_template = PipelineTemplate.objects.create(
            name="Community Template",
            code="community-template",
            source_pipeline=pipeline2,
            workspace=ws,
            validated_at=None,
        )

        # Test filtering for validated templates only
        response = self.run_query(
            """
            query($onlyValidated: Boolean) {
                pipelineTemplates(page: 1, perPage: 10, onlyValidated: $onlyValidated) {
                    items {
                        id
                        name
                        validatedAt
                    }
                }
            }
            """,
            {"onlyValidated": True},
        )

        items = response["data"]["pipelineTemplates"]["items"]
        item_ids = [item["id"] for item in items]

        self.assertIn(str(validated_template.id), item_ids)
        self.assertNotIn(str(community_template.id), item_ids)

        # Test filtering for community templates only
        response = self.run_query(
            """
            query($onlyValidated: Boolean) {
                pipelineTemplates(page: 1, perPage: 10, onlyValidated: $onlyValidated) {
                    items {
                        id
                        name
                        validatedAt
                    }
                }
            }
            """,
            {"onlyValidated": False},
        )

        items = response["data"]["pipelineTemplates"]["items"]
        item_ids = [item["id"] for item in items]

        self.assertNotIn(str(validated_template.id), item_ids)
        self.assertIn(str(community_template.id), item_ids)

        # Test showing all templates (no filter)
        response = self.run_query(
            """
            query {
                pipelineTemplates(page: 1, perPage: 10) {
                    items {
                        id
                        name
                        validatedAt
                    }
                }
            }
            """
        )

        items = response["data"]["pipelineTemplates"]["items"]
        item_ids = [item["id"] for item in items]

        self.assertIn(str(validated_template.id), item_ids)
        self.assertIn(str(community_template.id), item_ids)
