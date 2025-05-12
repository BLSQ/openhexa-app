from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.datasets.models import Dataset
from hexa.files.backends.base import StorageObject
from hexa.pipeline_templates.models import PipelineTemplate
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import User
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
        cls.WORKSPACE1 = Workspace.objects.create(
            name="Workspace 1",
            slug="workspace1",
            description="First workspace",
            db_name="db_workspace1",
            bucket_name="bucket_workspace1",
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

        cls.DATASET1 = Dataset.objects.create(
            name="Dataset",
            slug="dataset",
            description="First dataset",
            workspace=cls.WORKSPACE1,
        )
        cls.DATASET2 = Dataset.objects.create(
            name="Dataset 2",
            slug="dataset-2",
            description="Second dataset",
            workspace=cls.WORKSPACE2,
        )
        cls.DATASET3 = Dataset.objects.create(
            name="Dataset 3",
            slug="dataset-3",
            description="Third dataset (user not part of)",
            workspace=cls.WORKSPACE3,
        )

        cls.PIPELINE1 = Pipeline.objects.create(
            name="Pipeline 1",
            code="pipeline-1",
            description="First pipeline",
            workspace=cls.WORKSPACE1,
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
        )
        cls.TEMPLATE2 = PipelineTemplate.objects.create(
            name="Template 2",
            code="template-2",
            description="Second template",
            source_pipeline=cls.PIPELINE2,
        )
        cls.TEMPLATE3 = PipelineTemplate.objects.create(
            name="Template 3",
            code="template-3",
            description="Third template",
            source_pipeline=cls.PIPELINE3,
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
        self.assertEqual(response["data"]["searchPipelineTemplates"]["totalPages"], 2)
        self.assertEqual(response["data"]["searchPipelineTemplates"]["totalItems"], 3)

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
        self.assertEqual(
            response["data"]["searchFiles"]["items"][0],
            {
                "file": {"name": "file1", "path": "file1"},
                "score": 1.0,
                "workspace": {"name": "Workspace 1"},
            },
        )
        self.assertEqual(
            response["data"]["searchFiles"]["items"][1],
            {
                "file": {"name": "file2", "path": "file2"},
                "score": 0.5,
                "workspace": {"name": "Workspace 1"},
            },
        )

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
