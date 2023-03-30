from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.files.tests.mocks.mockgcp import mock_gcp_storage
from hexa.pipelines.models import Pipeline, PipelineRun, PipelineRunState
from hexa.user_management.models import Feature, FeatureFlag, User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class PipelinesV2Test(GraphQLTestCase):
    USER_ROOT = None
    USER_NOOB = None
    WS1 = None
    WS2 = None

    @classmethod
    @mock_gcp_storage
    def setUpTestData(cls):
        cls.USER_ROOT = User.objects.create_user(
            "root@bluesquarehub.com",
            "standardpassword",
            is_superuser=True,
        )
        cls.USER_NOOB = User.objects.create_user(
            "noob@bluesquarehub.com",
            "standardpassword",
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_NOOB
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
        cls.WORKSPACE2_MEMBERSHIP_1 = WorkspaceMembership.objects.create(
            workspace=cls.WS2,
            user=cls.USER_NOOB,
            role=WorkspaceMembershipRole.EDITOR,
        )

    def test_create_pipeline(self):
        self.assertEqual(0, len(Pipeline.objects.all()))

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
                mutation createPipeline($input: CreatePipelineInput!) {
                    createPipeline(input: $input) {
                        success errors pipeline {name code}
                    }
                }
            """,
            {
                "input": {
                    "code": "new_pipeline",
                    "name": "MonBeauPipeline",
                    "workspaceSlug": self.WS1.slug,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipeline": {"name": "MonBeauPipeline", "code": "new_pipeline"},
            },
            r["data"]["createPipeline"],
        )
        self.assertEqual(1, len(Pipeline.objects.all()))
        self.assertEqual(1, len(Pipeline.objects.filter_for_user(self.USER_ROOT)))

    def test_list_pipelines(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline()

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
              query {
                  pipelines {
                    items {
                      code
                      workspace { name slug }
                    }
                  }
              }
            """
        )
        self.assertEqual(1, len(r["data"]["pipelines"]["items"]))

        r = self.run_query(
            """
            query ($workspaceSlug: String!) {
                pipelines (workspaceSlug: $workspaceSlug) {
                    items {
                        code
                        workspace {
                            name
                        }
                    }
                }
            }""",
            {"workspaceSlug": self.WS1.slug},
        )
        self.assertEqual(1, len(r["data"]["pipelines"]["items"]))
        self.assertEqual(
            {"code": "new_pipeline", "workspace": {"name": "WS1"}},
            r["data"]["pipelines"]["items"][0],
        )

    def test_create_pipeline_version(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline()
        self.assertEqual(1, len(Pipeline.objects.all()))

        code1 = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first().code
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    version
                }
            }""",
            {
                "input": {
                    "code": code1,
                    "workspaceSlug": self.WS1.slug,
                    "entrypoint": "pm",
                    "parameters": {},
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(
            {"success": True, "version": 1, "errors": []}, r["data"]["uploadPipeline"]
        )

    def test_delete_pipeline(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline()
        self.assertEqual(1, len(Pipeline.objects.all()))

        id1 = Pipeline.objects.filter(workspace=self.WS1).first().id
        self.client.force_login(self.USER_NOOB)
        r = self.run_query(
            """
                mutation deletePipeline($input: DeletePipelineInput!) {
                    deletePipeline(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"id": str(id1)}},
        )

        self.assertEqual(False, r["data"]["deletePipeline"]["success"])
        self.assertEqual(["PIPELINE_NOT_FOUND"], r["data"]["deletePipeline"]["errors"])

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
                mutation deletePipeline($input: DeletePipelineInput!) {
                    deletePipeline(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"id": str(id1)}},
        )
        self.assertEqual(True, r["data"]["deletePipeline"]["success"])
        self.assertEqual(0, len(Pipeline.objects.all()))

    def test_pipeline_new_run(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline_version()
        self.assertEqual(1, len(Pipeline.objects.all()))

        id1 = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first().id

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
            mutation runPipeline($input: RunPipelineInput!) {
                runPipeline(input: $input) {
                    success
                    errors
                    run {id status}
                }
            }
            """,
            {"input": {"id": str(id1), "config": {}}},
        )
        self.assertEqual(True, r["data"]["runPipeline"]["success"])
        self.assertEqual(
            PipelineRunState.QUEUED, r["data"]["runPipeline"]["run"]["status"]
        )
        self.assertEqual(1, len(PipelineRun.objects.all()))

    def test_pipeline_by_code(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).first()
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    name
                }
            }
        """,
            {
                "code": "new_pipeline",
                "workspaceSlug": self.WS1.slug,
            },
        )

        self.assertEqual(
            {"id": str(pipeline.id), "code": "new_pipeline", "name": "MonBeauPipeline"},
            r["data"]["pipelineByCode"],
        )

        self.client.force_login(self.USER_NOOB)
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    name
                }
            }
        """,
            {
                "code": "new_pipeline",
                "workspaceSlug": self.WS1.slug,
            },
        )

        self.assertEqual(
            None,
            r["data"]["pipelineByCode"],
        )
