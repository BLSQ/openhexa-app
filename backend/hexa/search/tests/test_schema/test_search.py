from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.datasets.models import Dataset
from hexa.files.backends.base import StorageObject
from hexa.pipeline_templates.models import PipelineTemplate
from hexa.pipelines.models import Pipeline
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


class SearchResolversTest(GraphQLTestCase):
    USER = None
    WORKSPACE1 = None
    WORKSPACE2 = None
    WORKSPACE3 = None
    DATASET1 = None
    DATASET2 = None
    PIPELINE1 = None
    PIPELINE2 = None
    TEMPLATE1 = None
    TEMPLATE2 = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "user@bluesquarehub.com",
            "standardpassword",
            is_superuser=False,
        )
        cls.ADMIN_USER = User.objects.create_user(
            "admin@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        cls.ORGANIZATION = Organization.objects.create(
            name="Test Organization",
        )
        OrganizationMembership.objects.create(
            organization=cls.ORGANIZATION,
            user=cls.USER,
            role=OrganizationMembershipRole.MEMBER,
        )
        cls.WORKSPACE1 = Workspace.objects.create(
            name="Workspace 1",
            slug="workspace1",
            description="First workspace",
            db_name="db_workspace1",
            bucket_name="bucket_workspace1",
            organization=cls.ORGANIZATION,
        )
        cls.WORKSPACE2 = Workspace.objects.create(
            name="Workspace 2",
            slug="workspace2",
            description="Second workspace",
            db_name="db_workspace2",
            bucket_name="bucket_workspace2",
        )
        cls.WORKSPACE3 = Workspace.objects.create(
            name="Workspace 3",
            slug="workspace3",
            description="Third workspace (user not part of)",
            db_name="db_workspace3",
            bucket_name="bucket_workspace3",
        )

        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE1,
            user=cls.USER,
            role=WorkspaceMembershipRole.EDITOR,
        )
        WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE2,
            user=cls.USER,
            role=WorkspaceMembershipRole.VIEWER,
        )

        cls.DATASET1 = Dataset.objects.create_if_has_perm(
            principal=cls.ADMIN_USER,
            name="Dataset",
            description="First dataset",
            workspace=cls.WORKSPACE1,
        )
        cls.DATASET2 = Dataset.objects.create_if_has_perm(
            principal=cls.ADMIN_USER,
            name="Dataset 2",
            description="Second dataset",
            workspace=cls.WORKSPACE2,
        )
        cls.DATASET3 = Dataset.objects.create_if_has_perm(
            principal=cls.ADMIN_USER,
            name="Dataset 3",
            description="Third dataset (user not part of)",
            workspace=cls.WORKSPACE3,
        )

        cls.PIPELINE1 = Pipeline.objects.create(
            name="Pipeline 1",
            code="pipeline-1",
            description="First pipeline",
            workspace=cls.WORKSPACE1,
            functional_type="computation",
        )
        cls.PIPELINE2 = Pipeline.objects.create(
            name="Pipeline 2",
            code="pipeline-2",
            description="Second pipeline",
            workspace=cls.WORKSPACE2,
        )
        cls.PIPELINE3 = Pipeline.objects.create(
            name="Pipeline 3",
            code="pipeline-3",
            description="Third pipeline (user not part of)",
            workspace=cls.WORKSPACE3,
        )

        cls.TEMPLATE1 = PipelineTemplate.objects.create(
            name="Template",
            code="template",
            description="First template",
            source_pipeline=cls.PIPELINE1,
            workspace=cls.WORKSPACE1,
        )
        cls.TEMPLATE2 = PipelineTemplate.objects.create(
            name="Template 2",
            code="template-2",
            description="Second template",
            source_pipeline=cls.PIPELINE2,
            workspace=cls.WORKSPACE2,
        )
        cls.TEMPLATE3 = PipelineTemplate.objects.create(
            name="Template 3",
            code="template-3",
            description="Third template",
            source_pipeline=cls.PIPELINE3,
            workspace=cls.WORKSPACE3,
        )

    def test_search_datasets(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            """
            query searchDatasets($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchDatasets(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        dataset {
                            name
                            slug
                        }
                        score
                    }
                }
            }
            """,
            {
                "query": "Dataset",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )
        self.assertEqual(
            response["data"]["searchDatasets"]["items"],
            [
                {"dataset": {"name": "Dataset", "slug": "dataset"}, "score": 1},
                {"dataset": {"name": "Dataset 2", "slug": "dataset-2"}, "score": 0.5},
            ],
        )

    def test_search_datasets_with_organization_id(self):
        self.client.force_login(self.USER)

        response = self.run_query(
            """
            query searchDatasets($query: String!, $page: Int, $perPage: Int, $organizationId: UUID!) {
                searchDatasets(query: $query, page: $page, perPage: $perPage, organizationId: $organizationId) {
                    items {
                        dataset {
                            name
                            slug
                        }
                        score
                    }
                }
            }
            """,
            {
                "query": "Dataset",
                "page": 1,
                "perPage": 10,
                "organizationId": str(self.ORGANIZATION.id),
            },
        )
        self.assertEqual(
            response["data"]["searchDatasets"]["items"],
            [
                {"dataset": {"name": "Dataset", "slug": "dataset"}, "score": 1},
            ],
        )

    def test_search_pipelines(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            """
            query searchPipelines($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchPipelines(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        pipeline {
                            name
                            code
                        }
                        score
                    }
                }
            }
            """,
            {
                "query": "pipeline 1",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )
        self.assertEqual(
            response["data"]["searchPipelines"]["items"],
            [{"pipeline": {"name": "Pipeline 1", "code": "pipeline-1"}, "score": 1}],
        )

    def test_search_pipelines_by_functional_type(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            """
            query searchPipelines($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchPipelines(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        pipeline {
                            name
                            code
                            functionalType
                        }
                        score
                    }
                }
            }
            """,
            {
                "query": "computation",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )
        self.assertEqual(
            response["data"]["searchPipelines"]["items"],
            [
                {
                    "pipeline": {
                        "name": "Pipeline 1",
                        "code": "pipeline-1",
                        "functionalType": "computation",
                    },
                    "score": 1.0,
                }
            ],
        )

    def test_search_pipelines_by_partial_functional_type(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            """
            query searchPipelines($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchPipelines(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        pipeline {
                            name
                            code
                            functionalType
                        }
                        score
                    }
                }
            }
            """,
            {
                "query": "comp",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )
        self.assertEqual(
            response["data"]["searchPipelines"]["items"],
            [
                {
                    "pipeline": {
                        "name": "Pipeline 1",
                        "code": "pipeline-1",
                        "functionalType": "computation",
                    },
                    "score": 0.5,
                }
            ],
        )

    def test_search_pipeline_templates(self):
        self.client.force_login(self.USER)
        response = self.run_query(
            """
            query searchPipelineTemplates($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchPipelineTemplates(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        pipelineTemplate {
                            name
                            code
                        }
                        score
                    }
                    totalPages
                    totalItems
                }
            }
            """,
            {
                "query": "Template",
                "page": 1,
                "perPage": 2,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )
        self.assertEqual(
            response["data"]["searchPipelineTemplates"]["items"],
            [
                {
                    "pipelineTemplate": {"name": "Template", "code": "template"},
                    "score": 1,
                },
                {
                    "pipelineTemplate": {"name": "Template 2", "code": "template-2"},
                    "score": 0.5,
                },
            ],
        )
        self.assertEqual(response["data"]["searchPipelineTemplates"]["totalPages"], 1)
        self.assertEqual(response["data"]["searchPipelineTemplates"]["totalItems"], 2)

    def test_search_pipeline_templates_by_tag(self):
        self.client.force_login(self.USER)

        tag = Tag.objects.create(name="data-analysis")
        self.TEMPLATE1.tags.add(tag)

        response = self.run_query(
            """
            query searchPipelineTemplates($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchPipelineTemplates(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        pipelineTemplate {
                            name
                            code
                        }
                        score
                    }
                }
            }
            """,
            {
                "query": "data-analysis",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )
        self.assertEqual(
            response["data"]["searchPipelineTemplates"]["items"],
            [
                {
                    "pipelineTemplate": {"name": "Template", "code": "template"},
                    "score": 1,
                },
            ],
        )

    def test_search_pipelines_with_multiple_tags_no_duplicates(self):
        """Test that a pipeline with multiple tags appears only once in search results."""
        self.client.force_login(self.USER)

        tag1 = Tag.objects.create(name="etl")
        tag2 = Tag.objects.create(name="etl-process")
        tag3 = Tag.objects.create(name="etl-job")
        self.PIPELINE1.tags.add(tag1, tag2, tag3)

        response = self.run_query(
            """
            query searchPipelines($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchPipelines(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        pipeline {
                            name
                            code
                        }
                        score
                    }
                    totalItems
                }
            }
            """,
            {
                "query": "etl",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )
        self.assertEqual(response["data"]["searchPipelines"]["totalItems"], 1)
        self.assertEqual(
            response["data"]["searchPipelines"]["items"],
            [
                {
                    "pipeline": {"name": "Pipeline 1", "code": "pipeline-1"},
                    "score": 1,
                },
            ],
        )

    def test_search_pipeline_templates_with_multiple_tags_no_duplicates(self):
        """Test that a pipeline template with multiple tags appears only once in search results."""
        self.client.force_login(self.USER)

        tag1 = Tag.objects.create(name="reporting")
        tag2 = Tag.objects.create(name="reporting-tool")
        tag3 = Tag.objects.create(name="reporting-dashboard")
        self.TEMPLATE1.tags.add(tag1, tag2, tag3)

        response = self.run_query(
            """
            query searchPipelineTemplates($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchPipelineTemplates(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        pipelineTemplate {
                            name
                            code
                        }
                        score
                    }
                    totalItems
                }
            }
            """,
            {
                "query": "reporting",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )
        self.assertEqual(response["data"]["searchPipelineTemplates"]["totalItems"], 1)
        self.assertEqual(
            response["data"]["searchPipelineTemplates"]["items"],
            [
                {
                    "pipelineTemplate": {"name": "Template", "code": "template"},
                    "score": 1,
                },
            ],
        )

    def test_search_pipeline_templates_organization_wide(self):
        """Test that searchPipelineTemplates returns templates from entire organization, not just specific workspaces."""
        self.client.force_login(self.USER)

        ws_org_a = Workspace.objects.create(
            name="Org Workspace A",
            slug="org-workspace-a",
            description="First workspace in test org",
            db_name="db_org_workspace_a",
            bucket_name="bucket_org_workspace_a",
            organization=self.ORGANIZATION,
        )
        ws_org_b = Workspace.objects.create(
            name="Org Workspace B",
            slug="org-workspace-b",
            description="Second workspace in test org",
            db_name="db_org_workspace_b",
            bucket_name="bucket_org_workspace_b",
            organization=self.ORGANIZATION,
        )

        WorkspaceMembership.objects.create(
            workspace=ws_org_a,
            user=self.USER,
            role=WorkspaceMembershipRole.EDITOR,
        )
        WorkspaceMembership.objects.create(
            workspace=ws_org_b,
            user=self.USER,
            role=WorkspaceMembershipRole.EDITOR,
        )

        pipeline_a = Pipeline.objects.create(
            name="Pipeline A", code="pipeline-a", workspace=ws_org_a
        )
        pipeline_b = Pipeline.objects.create(
            name="Pipeline B", code="pipeline-b", workspace=ws_org_b
        )

        PipelineTemplate.objects.create(
            name="Org Template A",
            code="org-template-a",
            source_pipeline=pipeline_a,
            workspace=ws_org_a,
        )
        PipelineTemplate.objects.create(
            name="Org Template B",
            code="org-template-b",
            source_pipeline=pipeline_b,
            workspace=ws_org_b,
        )

        response = self.run_query(
            """
            query searchPipelineTemplates($query: String!, $page: Int, $perPage: Int, $organizationId: UUID!) {
                searchPipelineTemplates(query: $query, page: $page, perPage: $perPage, organizationId: $organizationId) {
                    items {
                        pipelineTemplate {
                            name
                            code
                        }
                        score
                    }
                    totalItems
                }
            }
            """,
            {
                "query": "Org Template",
                "page": 1,
                "perPage": 10,
                "organizationId": str(self.ORGANIZATION.id),
            },
        )

        self.assertEqual(response["data"]["searchPipelineTemplates"]["totalItems"], 2)
        template_codes = {
            item["pipelineTemplate"]["code"]
            for item in response["data"]["searchPipelineTemplates"]["items"]
        }
        self.assertEqual(template_codes, {"org-template-a", "org-template-b"})

    @patch("hexa.files.storage.list_bucket_objects")
    def test_search_files(self, mock_list_bucket_objects):
        self.client.force_login(self.USER)

        mock_list_bucket_objects.return_value.items = [
            StorageObject(
                name="file1", key="file1", path="file1", type="file", size=100
            ),
            StorageObject(
                name="file2", key="file2", path="file2", type="file", size=200
            ),
        ]

        response = self.run_query(
            """
            query searchFiles($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchFiles(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        file {
                            name
                            path
                        }
                        workspace {
                            name
                        }
                        score
                    }
                }
            }
            """,
            {
                "query": "file1",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )

        self.assertEqual(
            len(response["data"]["searchFiles"]["items"]),
            4,  # 2 files * 2 workspaces
        )

        items = response["data"]["searchFiles"]["items"]
        expected_items = [
            {
                "file": {"name": "file1", "path": "file1"},
                "score": 1.0,
                "workspace": {"name": "Workspace 1"},
            },
            {
                "file": {"name": "file2", "path": "file2"},
                "score": 0.5,
                "workspace": {"name": "Workspace 1"},
            },
        ]

        for expected_item in expected_items:
            self.assertIn(expected_item, items)

    @patch("hexa.search.schema.queries.get_database_definition")
    def test_search_database_tables(self, mock_get_database_definition):
        self.client.force_login(self.USER)

        mock_get_database_definition.return_value = [
            {"name": "table"},
            {"name": "table2"},
        ]

        response = self.run_query(
            """
            query searchDatabaseTables($query: String!, $page: Int, $perPage: Int, $workspaceSlugs: [String]!) {
                searchDatabaseTables(query: $query, page: $page, perPage: $perPage, workspaceSlugs: $workspaceSlugs) {
                    items {
                        databaseTable {
                            name
                        }
                        workspace {
                            name
                        }
                        score
                    }
                }
            }
            """,
            {
                "query": "table",
                "page": 1,
                "perPage": 10,
                "workspaceSlugs": ["workspace1", "workspace2"],
            },
        )

        self.assertEqual(
            response["data"]["searchDatabaseTables"]["items"],
            [
                {
                    "databaseTable": {"name": "table"},
                    "workspace": {"name": "Workspace 1"},
                    "score": 1.0,
                },
                {
                    "databaseTable": {"name": "table2"},
                    "workspace": {"name": "Workspace 1"},
                    "score": 0.5,
                },
                {
                    "databaseTable": {"name": "table"},
                    "workspace": {"name": "Workspace 2"},
                    "score": 1.0,
                },
                {
                    "databaseTable": {"name": "table2"},
                    "workspace": {"name": "Workspace 2"},
                    "score": 0.5,
                },
            ],
        )
