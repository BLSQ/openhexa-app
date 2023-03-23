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
            f"""
              mutation {{
                  createPipeline(input: {{
                      name: "MonBeauPipeline",
                      workspaceSlug: "{self.WS1.slug}"
                  }})
                  {{
                      success
                      errors
                      pipeline {{
                          id
                      }}
                  }}
              }}
            """
        )
        self.assertEqual(True, r["data"]["createPipeline"]["success"])
        self.assertEqual(1, len(Pipeline.objects.all()))

        self.client.force_login(self.USER_NOOB)
        r = self.run_query(
            f"""
              mutation {{
                  createPipeline(input: {{
                      name: "UnBienJoliTuyau"
                      workspaceSlug: "{self.WS2.slug}"
                  }})
                  {{
                      success
                      errors
                      pipeline {{
                          id
                      }}
                  }}
              }}
            """
        )
        self.assertEqual(True, r["data"]["createPipeline"]["success"])
        self.assertEqual(2, len(Pipeline.objects.all()))

        self.assertEqual(2, len(Pipeline.objects.filter_for_user(self.USER_ROOT)))
        self.assertEqual(1, len(Pipeline.objects.filter_for_user(self.USER_NOOB)))

    def test_list_pipelines(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline()

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
              query {
                  pipelines {
                    items {
                      name
                      workspace { name slug }
                    }
                  }
              }
            """
        )
        self.assertEqual(2, len(r["data"]["pipelines"]["items"]))

        r = self.run_query(
            f"""
              query {{
                  pipelines(workspaceSlug: "{self.WS1.slug}") {{
                    items {{
                      name
                      workspace {{ name }}
                    }}
                  }}
              }}
            """
        )
        self.assertEqual(1, len(r["data"]["pipelines"]["items"]))
        self.assertEqual(
            {"name": "MonBeauPipeline", "workspace": {"name": "WS1"}},
            r["data"]["pipelines"]["items"][0],
        )

    def test_create_pipeline_version(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline()
        self.assertEqual(2, len(Pipeline.objects.all()))

        name1 = Pipeline.objects.filter_for_user(user=self.USER_NOOB).first().name
        self.client.force_login(self.USER_NOOB)

        r = self.run_query(
            f"""
            mutation {{
              uploadPipeline(
                input: {{
                    name: "{name1}",
                    entrypoint: "pm",
                    parameters: {{}},
                    zipfile: ""
                }}
              )
              {{ success errors version }}
            }}
            """
        )
        self.assertEqual(True, r["data"]["uploadPipeline"]["success"])

    def test_delete_pipeline(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline()
        self.assertEqual(2, len(Pipeline.objects.all()))

        id1 = Pipeline.objects.filter(workspace=self.WS1).first().id
        self.client.force_login(self.USER_NOOB)
        r = self.run_query(
            f'mutation {{ deletePipeline(input: {{ id: "{id1}" }}) {{ success errors }} }}'
        )

        self.assertEqual(False, r["data"]["deletePipeline"]["success"])
        self.assertEqual(["PIPELINE_NOT_FOUND"], r["data"]["deletePipeline"]["errors"])

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            f'mutation {{ deletePipeline(input: {{ id: "{id1}" }}) {{ success errors }} }}'
        )
        self.assertEqual(True, r["data"]["deletePipeline"]["success"])
        self.assertEqual(1, len(Pipeline.objects.all()))

    def test_pipeline_new_run(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline_version()
        self.assertEqual(2, len(Pipeline.objects.all()))

        id1 = Pipeline.objects.filter_for_user(user=self.USER_NOOB).first().id

        self.client.force_login(self.USER_NOOB)
        r = self.run_query(
            f"""
              mutation {{
                runPipeline(
                  input: {{
                    id: "{id1}" ,
                    config: "--cool-option"
                  }}
                )
                {{
                  success
                  errors
                  run {{
                    id
                    status
                  }}
                }}
              }}
            """
        )
        self.assertEqual(True, r["data"]["runPipeline"]["success"])
        self.assertEqual(
            PipelineRunState.QUEUED, r["data"]["runPipeline"]["run"]["status"]
        )
        self.assertEqual(1, len(PipelineRun.objects.all()))

        id = r["data"]["runPipeline"]["run"]["id"]
        run = PipelineRun.objects.get(id=id)
        self.assertEqual("--cool-option", run.config)
