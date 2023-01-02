from hexa.core.test import GraphQLTestCase
from hexa.pipelines.models import Pipeline, PipelineRun, PipelineRunState
from hexa.user_management.models import User


class PipelinesV2Test(GraphQLTestCase):
    USER_ROOT = None
    USER_NOOB = None

    @classmethod
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

    def test_create_pipeline(self):
        self.assertEqual(0, len(Pipeline.objects.all()))

        self.client.force_login(self.USER_NOOB)
        r = self.run_query(
            """
              mutation {
                  createPipeline(input: {
                      name: "MonBeauPipeline",
                      entrypoint: "hello_world",
                      parameters: {}
                  })
                  {
                      success
                      errors
                      pipeline {
                          id
                      }
                  }
              }
            """
        )
        self.assertEqual(True, r["data"]["createPipeline"]["success"])
        self.assertEqual(1, len(Pipeline.objects.all()))

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
              mutation {
                  createPipeline(input: {
                      name: "UnBienJoliTuyau",
                      entrypoint: "pm",
                      parameters: {}
                  })
                  {
                      success
                      errors
                      pipeline {
                          id
                      }
                  }
              }
            """
        )
        self.assertEqual(True, r["data"]["createPipeline"]["success"])
        self.assertEqual(2, len(Pipeline.objects.all()))

        self.assertEqual(2, len(Pipeline.objects.filter_for_user(self.USER_ROOT)))
        self.assertEqual(1, len(Pipeline.objects.filter_for_user(self.USER_NOOB)))

    def test_create_pipeline_version(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self.test_create_pipeline()
        self.assertEqual(2, len(Pipeline.objects.all()))

        name1 = Pipeline.objects.filter(user=self.USER_NOOB).first().name
        self.client.force_login(self.USER_NOOB)

        r = self.run_query(
            f"""
            mutation {{
              uploadPipeline(
                input: {{
                    name: "{name1}",
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

        id1 = Pipeline.objects.filter(user=self.USER_ROOT).first().id

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

        id1 = Pipeline.objects.filter(user=self.USER_NOOB).first().id

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
