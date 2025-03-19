import base64
import random
import string
import uuid
from io import StringIO
from unittest.mock import MagicMock, patch

from django import test
from django.conf import settings
from django.core import mail
from django.core.signing import Signer

from hexa.core.test import GraphQLTestCase
from hexa.files import storage
from hexa.files.backends.exceptions import NotFound
from hexa.pipelines.models import (
    Pipeline,
    PipelineNotificationLevel,
    PipelineRecipient,
    PipelineRun,
    PipelineRunLogLevel,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineType,
)
from hexa.pipelines.tests.test_schema.fixtures_for_pipelines import (
    pipelines_example_parameters,
    pipelines_parameters_unvalid,
    pipelines_parameters_with_connections,
    pipelines_parameters_with_scalars,
)
from hexa.pipelines.utils import mail_run_recipients
from hexa.user_management.models import User
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
        cls.USER_LAMBDA = User.objects.create_user(
            "viewer@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
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
        cls.WORKSPACE1_MEMBERSHIP_2 = WorkspaceMembership.objects.create(
            workspace=cls.WS1,
            user=cls.USER_LAMBDA,
            role=WorkspaceMembershipRole.EDITOR,
        )
        cls.WORKSPACE1_MEMBERSHIP_3 = WorkspaceMembership.objects.create(
            workspace=cls.WS1,
            user=cls.USER_SABRINA,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def test_create_pipeline_without_name(self):
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
                    "workspaceSlug": self.WS1.slug,
                }
            },
        )
        self.assertIsNotNone(r["errors"])
        self.assertIn(
            "Field 'name' of required type 'String!' was not provided.",
            r["errors"][0]["message"],
        )

    def _create_pipeline(self, name):
        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
                mutation createPipeline($input: CreatePipelineInput!) {
                    createPipeline(input: $input) {
                        success errors pipeline {name}
                    }
                }
            """,
            {
                "input": {
                    "name": name,
                    "workspaceSlug": self.WS1.slug,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipeline": {"name": name},
            },
            r["data"]["createPipeline"],
        )

    def test_create_pipeline(self):
        self.assertEqual(0, len(Pipeline.objects.all()))

        self._create_pipeline("MonBeauPipeline")
        pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).get()

        self.assertEqual(1, len(Pipeline.objects.all()))
        self.assertEqual(1, len(Pipeline.objects.filter_for_user(self.USER_ROOT)))
        self.assertEqual(pipeline.type, PipelineType.ZIPFILE)

        return pipeline

    def test_create_pipeline_notebook_not_found(self):
        self.assertEqual(0, len(Pipeline.objects.all()))

        self.client.force_login(self.USER_ROOT)
        with patch(
            "hexa.pipelines.schema.mutations.get_bucket_object",
            MagicMock(),
        ) as bucket_mock:
            bucket_mock.side_effect = NotFound("File not found")
            r = self.run_query(
                """
                    mutation createPipeline($input: CreatePipelineInput!) {
                        createPipeline(input: $input) {
                            success 
                            errors 
                            pipeline {
                                name 
                                code
                            }
                        }
                    }
                """,
                {
                    "input": {
                        "name": "notebook.ipynb",
                        "workspaceSlug": self.WS1.slug,
                        "notebookPath": "notebook.ipynb",
                    }
                },
            )
            self.assertEqual(
                {"success": False, "errors": ["FILE_NOT_FOUND"], "pipeline": None},
                r["data"]["createPipeline"],
            )

    def test_create_pipeline_notebook(self):
        self.assertEqual(0, len(Pipeline.objects.all()))

        self.client.force_login(self.USER_ROOT)
        with patch(
            "hexa.pipelines.schema.mutations.get_bucket_object",
            MagicMock(),
        ) as bucket_mock:
            bucket_mock.return_value = {
                "name": "notebook.ipynb",
                "type": "file",
            }
            r = self.run_query(
                """
                    mutation createPipeline($input: CreatePipelineInput!) {
                        createPipeline(input: $input) {
                            success 
                            errors 
                            pipeline {
                                name 
                                code
                            }
                        }
                    }
                """,
                {
                    "input": {
                        "name": "notebook.ipynb",
                        "workspaceSlug": self.WS1.slug,
                        "notebookPath": "notebook.ipynb",
                    }
                },
            )

            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                    "pipeline": {"code": "notebook-ipynb", "name": "notebook.ipynb"},
                },
                r["data"]["createPipeline"],
            )
            self.assertEqual(1, len(Pipeline.objects.all()))
            pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).get()
            self.assertEqual(pipeline.type, PipelineType.NOTEBOOK)

    def test_list_pipelines(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        self._create_pipeline(name="Pipeline DHIS2")
        self._create_pipeline(name="Pipeline DHIS")
        self._create_pipeline(name="Pipeline S3")

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
            query ($workspaceSlug: String!, $name: String!) {
                pipelines (workspaceSlug: $workspaceSlug, name: $name) {
                    items {
                        code
                        workspace {
                            name
                        }
                    }
                }
            }""",
            {"workspaceSlug": self.WS1.slug, "name": "DHIS2"},
        )
        self.assertEqual(3, len(r["data"]["pipelines"]["items"]))
        self.assertEqual(
            {"code": "pipeline-dhis2", "workspace": {"name": "WS1"}},
            r["data"]["pipelines"]["items"][0],
        )
        self.assertEqual(
            {"code": "pipeline-dhis", "workspace": {"name": "WS1"}},
            r["data"]["pipelines"]["items"][1],
        )

    def test_create_pipeline_version(self, parameters=[], config={}):
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
                    pipelineVersion {
                        name
                    }
                }
            }""",
            {
                "input": {
                    "code": code1,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version 1",
                    "parameters": parameters,
                    "zipfile": "",
                    "config": config,
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "pipelineVersion": {"name": "Version 1"},
                "errors": [],
            },
            r["data"]["uploadPipeline"],
        )

    def test_create_pipeline_version_negative_timeout(self):
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
                }
            }""",
            {
                "input": {
                    "code": code1,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version 1",
                    "parameters": [],
                    "zipfile": "",
                    "timeout": -46800,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["INVALID_TIMEOUT_VALUE"]},
            r["data"]["uploadPipeline"],
        )

    def test_create_pipeline_version_timeout_greater_than_max_timeout(self):
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
                }
            }""",
            {
                "input": {
                    "code": code1,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version 1",
                    "parameters": [],
                    "zipfile": "",
                    "timeout": 46800,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["INVALID_TIMEOUT_VALUE"]},
            r["data"]["uploadPipeline"],
        )

    def test_create_pipeline_w_scalar_parameters(self):
        self.test_create_pipeline()
        self.assertEqual(1, len(Pipeline.objects.all()))

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    pipelineVersion { name }
                }
            }""",
            {
                "input": {
                    "code": pipeline.code,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version w parameters",
                    "parameters": pipelines_parameters_with_scalars,
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "pipelineVersion": {"name": "Version w parameters"},
                "errors": [],
            },
            r["data"]["uploadPipeline"],
        )

        r = self.run_query(
            """
            query ($id: UUID!) {
                pipeline(id: $id) {
                    currentVersion {
                        parameters {
                            code
                            name
                            type
                            help
                            default
                            multiple
                            required
                            choices
                        }
                    }
                }
            }
            """,
            {"id": str(pipeline.id)},
        )
        self.assertEqual(
            r["data"]["pipeline"]["currentVersion"],
            {
                "parameters": pipelines_parameters_with_scalars,
            },
        )

    def test_create_pipeline_w_conn_parameters(self):
        self.test_create_pipeline()
        self.assertEqual(1, len(Pipeline.objects.all()))

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    pipelineVersion { name }
                }
            }""",
            {
                "input": {
                    "code": pipeline.code,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version w parameters",
                    "parameters": pipelines_parameters_with_connections,
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "pipelineVersion": {"name": "Version w parameters"},
                "errors": [],
            },
            r["data"]["uploadPipeline"],
        )

        r = self.run_query(
            """
            query ($id: UUID!) {
                pipeline(id: $id) {
                    currentVersion {
                        parameters {
                            code
                            name
                            type
                            help
                            default
                            multiple
                            required
                            choices
                        }
                    }
                }
            }
            """,
            {"id": str(pipeline.id)},
        )
        self.assertEqual(
            r["data"]["pipeline"]["currentVersion"],
            {
                "parameters": pipelines_parameters_with_connections,
            },
        )

    def test_create_pipeline_w_unvalid_parameters(self):
        self.test_create_pipeline()
        self.assertEqual(1, len(Pipeline.objects.all()))

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    pipelineVersion { name }
                }
            }""",
            {
                "input": {
                    "code": pipeline.code,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version w parameters",
                    "parameters": pipelines_parameters_unvalid,
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "pipelineVersion": {"name": "Version w parameters"},
                "errors": [],
            },
            r["data"]["uploadPipeline"],
        )

        r = self.run_query(
            """
            query ($id: UUID!) {
                pipeline(id: $id) {
                    currentVersion {
                        parameters {
                            code
                            name
                            type
                            help
                            default
                            multiple
                            required
                            choices
                        }
                    }
                }
            }
            """,
            {"id": str(pipeline.id)},
        )
        self.assertEqual(
            "Enum 'ParameterType' cannot represent value: 'dhis3'",
            r["errors"][0]["message"],
        )

    def test_delete_pipeline_permission_denied(self):
        self.test_create_pipeline()
        id1 = Pipeline.objects.filter(workspace=self.WS1).first().id
        self.client.force_login(self.USER_SABRINA)
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
        self.assertEqual(["PERMISSION_DENIED"], r["data"]["deletePipeline"]["errors"])

    def test_delete_pipeline_queued_permission_denied(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.QUEUED
        run.save()

        pipeline = Pipeline.objects.filter(workspace=self.WS1).first()
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
                mutation deletePipeline($input: DeletePipelineInput!) {
                    deletePipeline(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"id": str(pipeline.id)}},
        )

        self.assertEqual(False, r["data"]["deletePipeline"]["success"])
        self.assertEqual(["PERMISSION_DENIED"], r["data"]["deletePipeline"]["errors"])

    def test_delete_pipeline_running_permission_denied(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.RUNNING
        run.save()

        pipeline = Pipeline.objects.filter(workspace=self.WS1).first()
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
                mutation deletePipeline($input: DeletePipelineInput!) {
                    deletePipeline(input: $input) {
                        success
                        errors
                    }
                }
            """,
            {"input": {"id": str(pipeline.id)}},
        )

        self.assertEqual(False, r["data"]["deletePipeline"]["success"])
        self.assertEqual(["PERMISSION_DENIED"], r["data"]["deletePipeline"]["errors"])

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
        self.assertEqual(0, len(Pipeline.objects.filter_for_user(user=self.USER_ROOT)))

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

    def test_pipeline_new_run_with_version_config(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        pipeline_version_config = {"param1": "param1_data"}
        self.test_create_pipeline_version(
            parameters=pipelines_example_parameters, config=pipeline_version_config
        )
        self.assertEqual(1, len(Pipeline.objects.all()))

        id1 = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first().id

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
            mutation runPipeline($input: RunPipelineInput!) {
                runPipeline(input: $input) {
                    success
                    errors
                    run {id status config}
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
        self.assertEqual(
            pipeline_version_config, r["data"]["runPipeline"]["run"]["config"]
        )

    def test_pipeline_new_run_with_pipeline_run_config(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        pipeline_version_config = {"param1": "param1_data"}
        self.test_create_pipeline_version(
            parameters=pipelines_example_parameters, config=pipeline_version_config
        )
        self.assertEqual(1, len(Pipeline.objects.all()))

        id1 = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first().id

        pipeline_run_config = {"param1": "param1_data_from_the_run_config"}
        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
            mutation runPipeline($input: RunPipelineInput!) {
                runPipeline(input: $input) {
                    success
                    errors
                    run {id status config}
                }
            }
            """,
            {"input": {"id": str(id1), "config": pipeline_run_config}},
        )
        self.assertEqual(True, r["data"]["runPipeline"]["success"])
        self.assertEqual(
            PipelineRunState.QUEUED, r["data"]["runPipeline"]["run"]["status"]
        )
        self.assertEqual(1, len(PipelineRun.objects.all()))
        self.assertEqual(pipeline_run_config, r["data"]["runPipeline"]["run"]["config"])

    def test_pipeline_new_run_with_empty_pipeline_run_config(self):
        self.assertEqual(0, len(PipelineRun.objects.all()))
        pipeline_version_config = {"param1": "param1_data", "param2": "param2_data"}
        self.test_create_pipeline_version(
            parameters=pipelines_example_parameters, config=pipeline_version_config
        )
        self.assertEqual(1, len(Pipeline.objects.all()))

        id1 = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first().id

        pipeline_run_config = {"param2": None}
        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
            mutation runPipeline($input: RunPipelineInput!) {
                runPipeline(input: $input) {
                    success
                    errors
                    run {id status config}
                }
            }
            """,
            {"input": {"id": str(id1), "config": pipeline_run_config}},
        )
        self.assertEqual(True, r["data"]["runPipeline"]["success"])
        self.assertEqual(
            PipelineRunState.QUEUED, r["data"]["runPipeline"]["run"]["status"]
        )
        self.assertEqual(1, len(PipelineRun.objects.all()))
        self.assertEqual(
            pipeline_version_config, r["data"]["runPipeline"]["run"]["config"]
        )

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
                "code": "monbeaupipeline",
                "workspaceSlug": self.WS1.slug,
            },
        )

        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": "monbeaupipeline",
                "name": "MonBeauPipeline",
            },
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
                "code": "monbeaupipeline",
                "workspaceSlug": self.WS1.slug,
            },
        )

        self.assertEqual(
            None,
            r["data"]["pipelineByCode"],
        )

    def test_pipeline_run_outputs(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )
        run.state = PipelineRunState.SUCCESS
        run.add_output(
            f"gs://{pipeline.workspace.bucket_name}/my_file", "file", "my_file"
        )
        run.add_output("uri2", "db", "my_table")
        storage.save_object(pipeline.workspace.bucket_name, "my_file", StringIO(""))
        with patch(
            "hexa.pipelines.schema.types.get_table_definition",
            return_value={"columns": [], "count": 0, "name": "my_table"},
        ):
            r = self.run_query(
                """
                query pipelineRunOutputs($id: UUID!) {
                    pipelineRun(id: $id) {
                        outputs {
                            __typename
                        }
                    }
                }
            """,
                {"id": str(run.id)},
            )
            self.assertEqual(
                r["data"]["pipelineRun"]["outputs"],
                [
                    {"__typename": "BucketObject"},
                    {"__typename": "DatabaseTable"},
                ],
            )

    def test_pipeline_run_file_output_failed(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )
        run.state = PipelineRunState.RUNNING
        run.save()

        access_token = Signer().sign_object(str(run.access_token))

        with patch(
            "hexa.pipelines.schema.mutations.get_bucket_object",
            MagicMock(),
        ) as bucket_mock:
            bucket_mock.side_effect = NotFound("File not found")

            r = self.run_query(
                """
                mutation addPipelineOutput ($input: AddPipelineOutputInput!) {
                    addPipelineOutput(input: $input) {
                          success
                          errors
                        }
                }""",
                {
                    "input": {
                        "uri": f"gs://{run.pipeline.workspace.bucket_name}",
                        "type": "file",
                        "name": "file_name",
                    }
                },
                headers={"HTTP_Authorization": f"bearer {access_token}"},
            )
            self.assertEqual(
                {"success": False, "errors": ["FILE_NOT_FOUND"]},
                r["data"]["addPipelineOutput"],
            )

    def test_pipeline_run_file_output(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )
        run.state = PipelineRunState.RUNNING
        run.save()

        access_token = Signer().sign_object(str(run.access_token))

        with patch(
            "hexa.pipelines.schema.mutations.get_bucket_object",
            MagicMock(),
        ) as bucket_mock:
            bucket_mock.return_value = {
                "name": "file_name",
                "type": "file",
            }

            r = self.run_query(
                """
                mutation addPipelineOutput ($input: AddPipelineOutputInput!) {
                    addPipelineOutput(input: $input) {
                          success
                          errors
                        }
                }""",
                {
                    "input": {
                        "uri": f"gs://{pipeline.workspace.bucket_name}/",
                        "type": "file",
                        "name": "file_name",
                    }
                },
                headers={"HTTP_Authorization": f"bearer {access_token}"},
            )
            self.assertEqual(
                {"success": True, "errors": []},
                r["data"]["addPipelineOutput"],
            )

    def test_pipeline_run_table_output_failed(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )
        run.state = PipelineRunState.RUNNING
        run.save()

        access_token = Signer().sign_object(str(run.access_token))

        with patch(
            "hexa.pipelines.schema.mutations.get_table_definition",
            MagicMock(),
        ) as table_mock:
            table_mock.return_value = None

            r = self.run_query(
                """
                mutation addPipelineOutput ($input: AddPipelineOutputInput!) {
                    addPipelineOutput(input: $input) {
                        success
                        errors
                        }
                }""",
                {
                    "input": {
                        "uri": f"postgresql://127.0.0.1/{run.pipeline.workspace.db_name}/random_table_name",
                        "type": "db",
                        "name": "random_table_name",
                    }
                },
                headers={"HTTP_Authorization": f"bearer {access_token}"},
            )
            self.assertEqual(
                {"success": False, "errors": ["TABLE_NOT_FOUND"]},
                r["data"]["addPipelineOutput"],
            )

    def test_pipeline_run_table_output(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )
        run.state = PipelineRunState.RUNNING
        run.save()

        access_token = Signer().sign_object(str(run.access_token))

        with patch(
            "hexa.pipelines.schema.mutations.get_table_definition",
            MagicMock(),
        ) as table_mock:
            table_mock.return_value = {
                "name": "table_name",
                "columns": [{"name": "column_1", "type": "str"}],
                "count": 10,
                "workspace": self.WS1,
            }

            r = self.run_query(
                """
                mutation addPipelineOutput ($input: AddPipelineOutputInput!) {
                    addPipelineOutput(input: $input) {
                        success
                        errors
                        }
                }""",
                {
                    "input": {
                        "uri": f"postgresql://127.0.0.1/{run.pipeline.workspace.db_name}/table_name",
                        "type": "db",
                        "name": "table_name",
                    }
                },
                headers={"HTTP_Authorization": f"bearer {access_token}"},
            )
            self.assertEqual(
                {"success": True, "errors": []},
                r["data"]["addPipelineOutput"],
            )

    def test_delete_pipeline_version_not_found(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters={},
        )

        r = self.run_query(
            """
            mutation deletePipelineVersion($input: DeletePipelineVersionInput!) {
                deletePipelineVersion(input: $input) {
                    success
                    errors
                }
            }
        """,
            {"input": {"id": str(uuid.uuid4())}},
        )
        self.assertEqual(
            {"success": False, "errors": ["PIPELINE_VERSION_NOT_FOUND"]},
            r["data"]["deletePipelineVersion"],
        )

    def test_delete_pipeline_version_permission_denied_no_admin(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_LAMBDA)

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters={},
        )
        pipeline_versions = pipeline.versions.all()

        r = self.run_query(
            """
            mutation deletePipelineVersion($input: DeletePipelineVersionInput!) {
                deletePipelineVersion(input: $input) {
                    success
                    errors
                }
            }
        """,
            {
                "input": {
                    "id": str(pipeline_versions.first().id),
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deletePipelineVersion"],
        )

    def test_delete_pipeline_version_permission_denied_one_version(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_LAMBDA)

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters={},
        )

        self.assertTrue(pipeline.versions.count() == 1)

        r = self.run_query(
            """
            mutation deletePipelineVersion($input: DeletePipelineVersionInput!) {
                deletePipelineVersion(input: $input) {
                    success
                    errors
                }
            }
        """,
            {
                "input": {
                    "id": str(pipeline.last_version.id),
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deletePipelineVersion"],
        )

    def test_delete_pipeline_version(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters={},
        )
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 2",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters={},
        )
        pipeline_versions = pipeline.versions.all()
        r = self.run_query(
            """
            mutation deletePipelineVersion($input: DeletePipelineVersionInput!) {
                deletePipelineVersion(input: $input) {
                    success
                    errors
                }
            }
        """,
            {
                "input": {
                    "id": str(pipeline_versions.first().id),
                }
            },
        )
        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deletePipelineVersion"],
        )

    def test_update_pipeline_public_webhook(self):
        self.test_create_pipeline_version()
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        self.assertEqual(pipeline.webhook_enabled, False)

        with patch("hexa.pipelines.models.TimestampSigner") as mocked_signer:
            random_string = base64.b64encode(
                "".join(random.choices(string.ascii_lowercase, k=10)).encode("utf-8")
            ).decode()

            signer = mocked_signer.return_value
            signer.sign.return_value = random_string
            encoded_token = base64.b64encode(random_string.encode("utf-8")).decode()

            r = self.run_query(
                """
                mutation updatePipeline($input: UpdatePipelineInput!) {
                    updatePipeline(input: $input) {
                        success
                        errors
                        pipeline {
                            webhookEnabled
                            webhookUrl
                        }
                    }
                }
            """,
                {
                    "input": {
                        "id": str(pipeline.id),
                        "webhookEnabled": True,
                    }
                },
            )

            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                    "pipeline": {
                        "webhookEnabled": True,
                        "webhookUrl": f"http://app.openhexa.test/pipelines/{encoded_token}/run",
                    },
                },
                r["data"]["updatePipeline"],
            )
            pipeline.refresh_from_db()
            self.assertEqual(pipeline.webhook_enabled, True)

    def test_delete_pipeline_workspace_members(self):
        self.test_create_pipeline_version()
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        PipelineRecipient.objects.create(pipeline=pipeline, user=self.USER_LAMBDA)
        self.WORKSPACE1_MEMBERSHIP_2.delete()

        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    recipients {
                      user {
                        displayName
                      }
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )

        self.assertEqual(
            {"recipients": []},
            r["data"]["pipelineByCode"],
        )

    @test.override_settings(NEW_FRONT_DOMAIN="localhost:3000")
    def test_mail_run_recipients_manual_trigger(self):
        self.client.force_login(self.USER_ROOT)
        self.test_pipeline_new_run()

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        version = pipeline.last_version

        PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_SABRINA,
            notification_level=PipelineNotificationLevel.ALL,
        )

        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        mail_run_recipients(run)
        self.assertEqual(
            f"Run report of {pipeline.code} ({run.state.label})",
            mail.outbox[0].subject,
        )
        self.assertListEqual([self.USER_SABRINA.email], mail.outbox[0].recipients())
        self.assertTrue(
            f"{settings.NEW_FRONTEND_DOMAIN}/workspaces/{pipeline.workspace.slug}/pipelines/{pipeline.code}/runs/{run.id}"
            in mail.outbox[0].body
        )

    @test.override_settings(NEW_FRONT_DOMAIN="localhost:3000")
    def test_mail_run_recipients_scheduled_trigger(self):
        self.client.force_login(self.USER_ROOT)
        self.test_pipeline_new_run()

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        version = pipeline.last_version

        PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_ROOT,
            notification_level=PipelineNotificationLevel.ALL,
        )
        PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_LAMBDA,
            notification_level=PipelineNotificationLevel.ALL,
        )

        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=version,
            trigger_mode=PipelineRunTrigger.SCHEDULED,
            config={},
        )

        mail_run_recipients(run)
        self.assertEqual(
            f"Run report of {pipeline.code} ({run.state.label})",
            mail.outbox[0].subject,
        )

        self.assertTrue(
            any(self.USER_LAMBDA.email in email.recipients() for email in mail.outbox)
        )
        self.assertTrue(
            any(self.USER_ROOT.email in email.recipients() for email in mail.outbox)
        )
        self.assertTrue(
            f"{settings.NEW_FRONTEND_DOMAIN}/workspaces/{pipeline.workspace.slug}/pipelines/{pipeline.code}/runs/{run.id}"
            in mail.outbox[0].body
        )

    def test_pipelines_permissions_schedule_true_no_param(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(self.USER_SABRINA).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters={},
        )
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    permissions {
                      schedule
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )
        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": pipeline.code,
                "permissions": {"schedule": True},
            },
            r["data"]["pipelineByCode"],
        )

    def test_pipelines_permissions_schedule_true(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(self.USER_SABRINA).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[
                {
                    "code": "param1",
                    "name": "Param 1",
                    "type": "string",
                    "help": "Param 1's Help",
                    "default": None,
                    "multiple": True,
                    "required": True,
                    "choices": ["Choice 1", "Choice 2"],
                }
            ],
        )
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    permissions {
                      schedule
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )
        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": pipeline.code,
                "permissions": {"schedule": False},
            },
            r["data"]["pipelineByCode"],
        )

    def test_pipelines_permissions_schedule_required_param_with_no_default_value(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(self.USER_SABRINA).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            zipfile=base64.b64decode("".encode("ascii")),
            name="Version 1",
            parameters=[
                {
                    "code": "param1",
                    "name": "Param 1",
                    "type": "string",
                    "help": "Param 1's Help",
                    "default": None,
                    "multiple": False,
                    "required": True,
                }
            ],
        )
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    permissions {
                      schedule
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )
        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": pipeline.code,
                "permissions": {"schedule": False},
            },
            r["data"]["pipelineByCode"],
        )

    def test_pipelines_permissions_schedule_required_param_with_no_default_value_with_version_config(
        self,
    ):
        self.test_create_pipeline()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(self.USER_SABRINA).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            zipfile=base64.b64decode("".encode("ascii")),
            name="Version 1",
            config={"param1": "value"},
            parameters=[
                {
                    "code": "param1",
                    "name": "Param 1",
                    "type": "string",
                    "help": "Param 1's Help",
                    "default": None,
                    "multiple": False,
                    "required": True,
                }
            ],
        )
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    permissions {
                      schedule
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )
        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": pipeline.code,
                "permissions": {"schedule": True},
            },
            r["data"]["pipelineByCode"],
        )

    def test_pipelines_permissions_schedule_required_param_empty_string(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(self.USER_SABRINA).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[
                {
                    "code": "param1",
                    "name": "Param 1",
                    "type": "string",
                    "help": "Param 1's Help",
                    "default": "",
                    "multiple": False,
                    "required": True,
                }
            ],
        )
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    permissions {
                      schedule
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )
        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": pipeline.code,
                "permissions": {"schedule": True},
            },
            r["data"]["pipelineByCode"],
        )

    def test_pipelines_permissions_schedule_not_required_param_with_value_none(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(self.USER_SABRINA).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[
                {
                    "code": "param1",
                    "name": "Param 1",
                    "type": "string",
                    "default": None,
                    "help": "Param 1's Help",
                    "multiple": False,
                    "required": True,
                }
            ],
        )
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    permissions {
                      schedule
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )
        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": pipeline.code,
                "permissions": {"schedule": False},
            },
            r["data"]["pipelineByCode"],
        )

    def test_pipelines_permissions_schedule_with_params_true(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[
                {
                    "code": "param1",
                    "name": "Param 1",
                    "type": "string",
                    "help": "Param 1's Help",
                    "default": "Default",
                    "multiple": True,
                    "required": True,
                    "choices": ["Choice 1", "Choice 2"],
                },
                {
                    "code": "param2",
                    "name": "Param 2",
                    "type": "int",
                    "help": "Param 2's Help",
                    "default": 2,
                    "multiple": False,
                    "required": True,
                },
                {
                    "code": "param3",
                    "name": "Param 3",
                    "type": "bool",
                    "help": "Param 3's Help",
                    "default": False,
                    "multiple": False,
                    "required": True,
                },
            ],
        )

        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    permissions {
                      schedule
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )
        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": pipeline.code,
                "permissions": {"schedule": True},
            },
            r["data"]["pipelineByCode"],
        )

    def test_pipelines_permissions_schedule_with_params_false(self):
        pipeline = self.test_create_pipeline()
        pipeline.upload_new_version(
            user=self.USER_LAMBDA,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[
                {
                    "code": "param1",
                    "name": "Param 1",
                    "type": "string",
                    "help": "Param 1's Help",
                    "multiple": True,
                    "required": True,
                    "choices": ["Choice 1", "Choice 2"],
                },
                {
                    "code": "param2",
                    "name": "Param 2",
                    "type": "int",
                    "help": "Param 2's Help",
                    "default": None,
                    "multiple": False,
                    "required": True,
                },
            ],
        )

        self.client.force_login(self.USER_LAMBDA)
        r = self.run_query(
            """
            query pipelineByCode($code: String!, $workspaceSlug: String!) {
                pipelineByCode(code: $code, workspaceSlug: $workspaceSlug) {
                    id
                    code
                    permissions {
                      schedule
                    }
                }
            }
        """,
            {
                "code": pipeline.code,
                "workspaceSlug": self.WS1.slug,
            },
        )
        self.assertEqual(
            {
                "id": str(pipeline.id),
                "code": pipeline.code,
                "permissions": {"schedule": False},
            },
            r["data"]["pipelineByCode"],
        )

    def test_upload_pipeline_parameters_not_supported(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).first()
        pipeline.schedule = "0 15 * * *"
        pipeline.save()

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }""",
            {
                "input": {
                    "code": pipeline.code,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version with parameters",
                    "parameters": [
                        {
                            "code": "param1",
                            "name": "Param 1",
                            "type": "string",
                            "help": "Param 1's Help",
                            "default": None,
                            "multiple": True,
                            "required": True,
                            "choices": ["Choice 1", "Choice 2"],
                        }
                    ],
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PIPELINE_DOES_NOT_SUPPORT_PARAMETERS"]},
            r["data"]["uploadPipeline"],
        )

    def test_upload_unschedulable_pipeline(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(self.USER_ROOT).first()

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }""",
            {
                "input": {
                    "code": pipeline.code,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version unschedulable",
                    "parameters": [
                        {
                            "code": "param1",
                            "name": "Param 1",
                            "type": "string",
                            "help": "Param 1's Help",
                            "default": None,
                            "multiple": True,
                            "required": True,
                            "choices": ["Choice 1", "Choice 2"],
                        }
                    ],
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["uploadPipeline"],
        )

    def test_pipeline_new_run_with_timeout(self):
        self.test_create_pipeline()

        code1 = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first().code
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                    pipelineVersion { name }
                }
            }""",
            {
                "input": {
                    "code": code1,
                    "workspaceSlug": self.WS1.slug,
                    "name": "Version with timeout",
                    "parameters": [],
                    "zipfile": "",
                    "timeout": 3600,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipelineVersion": {"name": "Version with timeout"},
            },
            r["data"]["uploadPipeline"],
        )

        id1 = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first().id

        self.client.force_login(self.USER_ROOT)
        r = self.run_query(
            """
            mutation runPipeline($input: RunPipelineInput!) {
                runPipeline(input: $input) {
                    success
                    errors
                    run {
                        timeout
                        status
                    }
                }
            }
            """,
            {"input": {"id": str(id1), "config": {}}},
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "run": {"timeout": 3600, "status": PipelineRunState.QUEUED},
            },
            r["data"]["runPipeline"],
        )
        self.assertEqual(1, len(PipelineRun.objects.all()))
        pipeline_run = PipelineRun.objects.first()
        self.assertEqual(pipeline_run.log_level, PipelineRunLogLevel.INFO)
        self.assertFalse(pipeline_run.send_mail_notifications)

    def test_pipeline_new_run_default_timeout(self):
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
                    run {
                        timeout
                        status
                    }
                }
            }
            """,
            {
                "input": {
                    "id": str(id1),
                    "config": {},
                    "sendMailNotifications": True,
                    "enableDebugLogs": True,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "run": {"timeout": 14400, "status": PipelineRunState.QUEUED},
            },
            r["data"]["runPipeline"],
        )
        self.assertEqual(1, len(PipelineRun.objects.all()))
        pipeline_run = PipelineRun.objects.first()
        self.assertEqual(pipeline_run.log_level, PipelineRunLogLevel.DEBUG)
        self.assertTrue(pipeline_run.send_mail_notifications)

    def test_stop_running_pipeline(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.SUCCESS
        run.save()

        r = self.run_query(
            """
            mutation stopPipeline($input: StopPipelineInput!) {
                stopPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"runId": str(run.id)}},
        )
        self.assertEqual(False, r["data"]["stopPipeline"]["success"])
        self.assertEqual(
            ["PIPELINE_ALREADY_COMPLETED"], r["data"]["stopPipeline"]["errors"]
        )

    def test_stop_pipeline_run_stopped(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.STOPPED
        run.save()

        r = self.run_query(
            """
            mutation stopPipeline($input: StopPipelineInput!) {
                stopPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"runId": str(run.id)}},
        )
        self.assertEqual(False, r["data"]["stopPipeline"]["success"])
        self.assertEqual(
            ["PIPELINE_ALREADY_STOPPED"], r["data"]["stopPipeline"]["errors"]
        )

    def test_stop_pipeline_run_terminating(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.TERMINATING
        run.save()

        r = self.run_query(
            """
            mutation stopPipeline($input: StopPipelineInput!) {
                stopPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"runId": str(run.id)}},
        )
        self.assertEqual(False, r["data"]["stopPipeline"]["success"])
        self.assertEqual(
            ["PIPELINE_ALREADY_STOPPED"], r["data"]["stopPipeline"]["errors"]
        )

    def test_stop_pipeline_run_denied(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_SABRINA)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.RUNNING
        run.save()

        r = self.run_query(
            """
            mutation stopPipeline($input: StopPipelineInput!) {
                stopPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"runId": str(run.id)}},
        )

        self.assertEqual(False, r["data"]["stopPipeline"]["success"])
        self.assertEqual(["PERMISSION_DENIED"], r["data"]["stopPipeline"]["errors"])

    def test_stop_pipeline_run(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=pipeline.last_version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
        )

        run.state = PipelineRunState.RUNNING
        run.save()

        r = self.run_query(
            """
            mutation stopPipeline($input: StopPipelineInput!) {
                stopPipeline(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"runId": str(run.id)}},
        )
        run.refresh_from_db()

        self.assertEqual(True, r["data"]["stopPipeline"]["success"])
        self.assertEqual(PipelineRunState.TERMINATING, run.state)
        self.assertEqual(self.USER_ROOT, run.stopped_by)

    def test_generate_pipeline_webhook_url_not_found(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            mutation generateWebhookPipelineUrl($input: GeneratePipelineWebhookUrlInput!) {
                generatePipelineWebhookUrl(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"id": str(uuid.uuid4())}},
        )

        self.assertEqual(
            {"success": False, "errors": ["PIPELINE_NOT_FOUND"]},
            r["data"]["generatePipelineWebhookUrl"],
        )

    def test_generate_pipeline_webhook_url_not_enabled(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        pipeline.webhook_enabled = False
        pipeline.save()

        r = self.run_query(
            """
            mutation generateWebhookPipelineUrl($input: GeneratePipelineWebhookUrlInput!) {
                generatePipelineWebhookUrl(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"id": str(pipeline.id)}},
        )

        self.assertEqual(
            {"success": False, "errors": ["WEBHOOK_NOT_ENABLED"]},
            r["data"]["generatePipelineWebhookUrl"],
        )

    def test_generate_pipeline_webhook_url(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.get(code="monbeaupipeline")
        pipeline.webhook_enabled = True
        pipeline.save()

        with patch("hexa.pipelines.models.TimestampSigner") as mocked_signer:
            random_string = base64.b64encode(
                "".join(random.choices(string.ascii_lowercase, k=10)).encode("utf-8")
            ).decode()

            signer = mocked_signer.return_value
            signer.sign.return_value = random_string
            encoded_token = base64.b64encode(random_string.encode("utf-8")).decode()

            r = self.run_query(
                """
                mutation generateWebhookPipelineUrl($input: GeneratePipelineWebhookUrlInput!) {
                    generatePipelineWebhookUrl(input: $input) {
                        success
                        errors
                        pipeline {
                         webhookUrl
                        }
                    }
                }
                """,
                {"input": {"id": str(pipeline.id)}},
            )

            self.assertEqual(
                {
                    "success": True,
                    "errors": [],
                    "pipeline": {
                        "webhookUrl": f"http://app.openhexa.test/pipelines/{encoded_token}/run"
                    },
                },
                r["data"]["generatePipelineWebhookUrl"],
            )

    def test_generate_pipeline_webhook_url_update_permission_denied(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.get(code="monbeaupipeline")

        r = self.run_query(
            """
            mutation generateWebhookPipelineUrl($input: GeneratePipelineWebhookUrlInput!) {
                generatePipelineWebhookUrl(input: $input) {
                    success
                    errors
                }
            }
            """,
            {"input": {"id": str(pipeline.id)}},
        )

        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["generatePipelineWebhookUrl"],
        )

    def test_add_pipeline_recipient_pipeline_not_found(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        r = self.run_query(
            """
            mutation addPipelineRecipient($input: CreatePipelineRecipientInput!) {
                addPipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "pipelineId": str(uuid.uuid4()),
                    "userId": str(self.USER_ROOT.id),
                    "notificationLevel": PipelineNotificationLevel.ALL,
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["PIPELINE_NOT_FOUND"]},
            r["data"]["addPipelineRecipient"],
        )

    def test_add_pipeline_recipient_user_not_found(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()

        r = self.run_query(
            """
            mutation addPipelineRecipient($input: CreatePipelineRecipientInput!) {
                addPipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "pipelineId": str(pipeline.id),
                    "userId": str(uuid.uuid4()),
                    "notificationLevel": PipelineNotificationLevel.ALL,
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["USER_NOT_FOUND"]},
            r["data"]["addPipelineRecipient"],
        )

    def test_add_pipeline_recipient_permission_denied(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_SABRINA).first()

        r = self.run_query(
            """
            mutation addPipelineRecipient($input: CreatePipelineRecipientInput!) {
                addPipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "pipelineId": str(pipeline.id),
                    "userId": str(self.USER_SABRINA.id),
                    "notificationLevel": PipelineNotificationLevel.ALL,
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["addPipelineRecipient"],
        )

    def test_add_pipeline_recipient_already_exists(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_SABRINA,
            notification_level=PipelineNotificationLevel.ERROR,
        )

        r = self.run_query(
            """
            mutation addPipelineRecipient($input: CreatePipelineRecipientInput!) {
                addPipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "pipelineId": str(pipeline.id),
                    "userId": str(self.USER_SABRINA.id),
                    "notificationLevel": PipelineNotificationLevel.ALL,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["ALREADY_EXISTS"]},
            r["data"]["addPipelineRecipient"],
        )

    def test_add_pipeline_recipient(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_SABRINA).first()

        r = self.run_query(
            """
            mutation addPipelineRecipient($input: CreatePipelineRecipientInput!) {
                addPipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "pipelineId": str(pipeline.id),
                    "userId": str(self.USER_SABRINA.id),
                    "notificationLevel": PipelineNotificationLevel.ALL,
                }
            },
        )
        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["addPipelineRecipient"],
        )

    def test_update_pipeline_recipient(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_SABRINA).first()

        recipient = PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_SABRINA,
            notification_level=PipelineNotificationLevel.ERROR,
        )

        r = self.run_query(
            """
            mutation updatePipelineRecipient($input: UpdatePipelineRecipientInput!) {
                updatePipelineRecipient(input: $input) {
                    success
                    errors
                    recipient {
                        notificationLevel
                    }
                }
            }
            """,
            {
                "input": {
                    "recipientId": str(recipient.id),
                    "notificationLevel": PipelineNotificationLevel.ALL,
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "recipient": {"notificationLevel": PipelineNotificationLevel.ALL},
            },
            r["data"]["updatePipelineRecipient"],
        )

    def test_update_pipeline_recipient_not_found(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_SABRINA).first()

        PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_SABRINA,
            notification_level=PipelineNotificationLevel.ERROR,
        )

        r = self.run_query(
            """
            mutation updatePipelineRecipient($input: UpdatePipelineRecipientInput!) {
                updatePipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "recipientId": str(uuid.uuid4()),
                    "notificationLevel": PipelineNotificationLevel.ALL,
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["RECIPIENT_NOT_FOUND"],
            },
            r["data"]["updatePipelineRecipient"],
        )

    def test_update_pipeline_recipient_permission_denied(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_SABRINA).first()

        recipient = PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_SABRINA,
            notification_level=PipelineNotificationLevel.ERROR,
        )

        r = self.run_query(
            """
            mutation updatePipelineRecipient($input: UpdatePipelineRecipientInput!) {
                updatePipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "recipientId": str(recipient.id),
                    "notificationLevel": PipelineNotificationLevel.ALL,
                }
            },
        )
        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["updatePipelineRecipient"],
        )

    def test_delete_pipeline_recipient_not_found(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_SABRINA).first()

        PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_SABRINA,
            notification_level=PipelineNotificationLevel.ERROR,
        )

        r = self.run_query(
            """
            mutation deletePipelineRecipient($input: DeletePipelineRecipientInput!) {
                deletePipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "recipientId": str(uuid.uuid4()),
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["RECIPIENT_NOT_FOUND"],
            },
            r["data"]["deletePipelineRecipient"],
        )

    def test_delete_pipeline_recipient_permission_denied(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_SABRINA).first()

        recipient = PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_SABRINA,
            notification_level=PipelineNotificationLevel.ERROR,
        )

        r = self.run_query(
            """
            mutation deletePipelineRecipient($input: DeletePipelineRecipientInput!) {
                deletePipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "recipientId": str(recipient.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            },
            r["data"]["deletePipelineRecipient"],
        )

    def test_delete_pipeline_recipient(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_SABRINA).first()

        recipient = PipelineRecipient.objects.create(
            pipeline=pipeline,
            user=self.USER_SABRINA,
            notification_level=PipelineNotificationLevel.ERROR,
        )

        r = self.run_query(
            """
            mutation deletePipelineRecipient($input: DeletePipelineRecipientInput!) {
                deletePipelineRecipient(input: $input) {
                    success
                    errors
                }
            }
            """,
            {
                "input": {
                    "recipientId": str(recipient.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
            },
            r["data"]["deletePipelineRecipient"],
        )

    def test_new_template_version_available(self):
        self.client.force_login(self.USER_ROOT)
        source_pipeline = Pipeline.objects.create(
            code="source_pipeline",
            workspace=self.WS1,
        )
        source_pipeline_version1 = source_pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[],
        )
        template, _ = source_pipeline.get_or_create_template(
            "Template", "template", "Description"
        )
        template_version1 = template.create_version(source_pipeline_version1)

        r = self.run_query(
            """
                mutation createPipelineFromTemplateVersion($input: CreatePipelineFromTemplateVersionInput!) {
                    createPipelineFromTemplateVersion(input: $input) {
                        success errors pipeline {id newTemplateVersions {versionNumber}}
                    }
                }
            """,
            {
                "input": {
                    "workspaceSlug": self.WS2.slug,
                    "pipelineTemplateVersionId": str(template_version1.id),
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipeline": {
                    "id": str(
                        r["data"]["createPipelineFromTemplateVersion"]["pipeline"]["id"]
                    ),
                    "newTemplateVersions": [],
                },
            },
            r["data"]["createPipelineFromTemplateVersion"],
        )

        source_version2 = source_pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 2",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[],
        )
        template.create_version(source_version2)

        r = self.run_query(
            """
            query ($id: UUID!) {
                pipeline(id: $id) {
                    newTemplateVersions {
                        versionNumber
                    }
                }
            }
            """,
            {
                "id": str(
                    r["data"]["createPipelineFromTemplateVersion"]["pipeline"]["id"]
                )
            },
        )
        self.assertEqual(
            [{"versionNumber": 2}], r["data"]["pipeline"]["newTemplateVersions"]
        )

    def test_upgrade_pipeline_version_from_template(self):
        self.test_create_pipeline_version()
        self.client.force_login(self.USER_ROOT)

        source_pipeline = Pipeline.objects.create(
            code="source_pipeline",
            workspace=self.WS1,
        )
        source_pipeline_version1 = source_pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[],
        )
        source_pipeline_version2 = source_pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 2",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[],
        )
        template, _ = source_pipeline.get_or_create_template(
            "Template", "template", "Description"
        )
        template_version1 = template.create_version(source_pipeline_version1)
        r = self.run_query(
            """
                mutation createPipelineFromTemplateVersion($input: CreatePipelineFromTemplateVersionInput!) {
                    createPipelineFromTemplateVersion(input: $input) {
                        success errors pipeline { id currentVersion { versionNumber } }
                    }
                }
            """,
            {
                "input": {
                    "workspaceSlug": self.WS2.slug,
                    "pipelineTemplateVersionId": str(template_version1.id),
                }
            },
        )
        self.assertEqual(
            1,
            r["data"]["createPipelineFromTemplateVersion"]["pipeline"][
                "currentVersion"
            ]["versionNumber"],
        )
        pipeline_id = r["data"]["createPipelineFromTemplateVersion"]["pipeline"]["id"]
        template.create_version(source_pipeline_version2)
        r = self.run_query(
            """
                mutation upgradePipelineVersionFromTemplate($input: UpgradePipelineVersionFromTemplateInput!) {
                    upgradePipelineVersionFromTemplate(input: $input) {
                        success errors pipelineVersion {versionNumber}
                    }
                }
            """,
            {
                "input": {
                    "pipelineId": pipeline_id,
                }
            },
        )

        self.assertEqual(
            True, r["data"]["upgradePipelineVersionFromTemplate"]["success"]
        )
        self.assertEqual([], r["data"]["upgradePipelineVersionFromTemplate"]["errors"])
        self.assertEqual(
            2,
            r["data"]["upgradePipelineVersionFromTemplate"]["pipelineVersion"][
                "versionNumber"
            ],
        )

    def _get_pipeline(self, pipeline_id):
        return self.run_query(
            """
                query ($id: UUID!) {
                    pipeline(id: $id) {
                        permissions {
                            createTemplateVersion { isAllowed }
                        }
                    }
                }
            """,
            {"id": str(pipeline_id)},
        )

    def test_permission_to_create_template_version(self):
        self.client.force_login(self.USER_ROOT)
        source_pipeline = Pipeline.objects.create(
            code="source_pipeline", workspace=self.WS1, type=PipelineType.NOTEBOOK
        )
        source_pipeline.upload_new_version(
            user=self.USER_ROOT,
            name="Version 1",
            zipfile=base64.b64decode("".encode("ascii")),
            parameters=[],
        )
        r = self._get_pipeline(source_pipeline.id)
        self.assertFalse(
            r["data"]["pipeline"]["permissions"]["createTemplateVersion"]["isAllowed"]
        )
        source_pipeline.type = PipelineType.ZIPFILE
        source_pipeline.save()
        r = self._get_pipeline(source_pipeline.id)
        self.assertTrue(
            r["data"]["pipeline"]["permissions"]["createTemplateVersion"]["isAllowed"]
        )
        template, _ = source_pipeline.get_or_create_template(
            "Template", "template", "Description"
        )
        template.create_version(source_pipeline.last_version)
        r = self._get_pipeline(source_pipeline.id)
        self.assertFalse(
            r["data"]["pipeline"]["permissions"]["createTemplateVersion"]["isAllowed"]
        )
