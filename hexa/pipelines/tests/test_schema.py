import base64
import uuid
from unittest.mock import patch

from django import test
from django.conf import settings
from django.core import mail

from hexa.core.test import GraphQLTestCase
from hexa.files.tests.mocks.mockgcp import mock_gcp_storage
from hexa.pipelines.models import (
    Pipeline,
    PipelineRecipient,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineVersion,
)
from hexa.pipelines.utils import mail_run_recipients
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
        cls.USER_LAMBDA = User.objects.create_user(
            "viewer@bluesquarehub.com",
            "standardpassword",
        )
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_NOOB
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.create(code="workspaces"), user=cls.USER_SABRINA
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
                    "parameters": [],
                    "zipfile": "",
                }
            },
        )
        self.assertEqual(
            {"success": True, "version": 1, "errors": []}, r["data"]["uploadPipeline"]
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
                    version
                }
            }""",
            {
                "input": {
                    "code": code1,
                    "workspaceSlug": self.WS1.slug,
                    "parameters": [],
                    "zipfile": "",
                    "timeout": -46800,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["INVALID_TIMEOUT_VALUE"], "version": None},
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
                    version
                }
            }""",
            {
                "input": {
                    "code": code1,
                    "workspaceSlug": self.WS1.slug,
                    "parameters": [],
                    "zipfile": "",
                    "timeout": 46800,
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["INVALID_TIMEOUT_VALUE"], "version": None},
            r["data"]["uploadPipeline"],
        )

    def test_create_pipeline_w_parameters(self):
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
                    version
                }
            }""",
            {
                "input": {
                    "code": pipeline.code,
                    "workspaceSlug": self.WS1.slug,
                    "parameters": [
                        {
                            "code": "param1",
                            "name": "Param 1",
                            "type": "string",
                            "help": "Param 1's Help",
                            "default": "default value",
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
            {"success": True, "version": 1, "errors": []}, r["data"]["uploadPipeline"]
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
                "parameters": [
                    {
                        "code": "param1",
                        "name": "Param 1",
                        "type": "string",
                        "help": "Param 1's Help",
                        "default": "default value",
                        "multiple": True,
                        "required": True,
                        "choices": ["Choice 1", "Choice 2"],
                    }
                ],
            },
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

    def test_delete_pipeline_version_pipeline_not_found(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
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
                    "pipelineId": str(uuid.uuid4()),
                    "versionId": str(pipeline_versions.first().id),
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PIPELINE_NOT_FOUND"]},
            r["data"]["deletePipelineVersion"],
        )

    def test_delete_pipeline_version_not_found(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
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
            {"input": {"pipelineId": str(pipeline.id), "versionId": str(uuid.uuid4())}},
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
                    "pipelineId": str(pipeline.id),
                    "versionId": str(pipeline_versions.first().id),
                }
            },
        )
        self.assertEqual(
            {"success": False, "errors": ["PERMISSION_DENIED"]},
            r["data"]["deletePipelineVersion"],
        )

    def test_delete_pipeline_version_permission_denied_one_version(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_ROOT)

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
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
                    "pipelineId": str(pipeline.id),
                    "versionId": str(pipeline_versions.first().id),
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
            zipfile=base64.b64decode("".encode("ascii")),
            parameters={},
        )
        pipeline.upload_new_version(
            user=self.USER_ROOT,
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
                    "pipelineId": str(pipeline.id),
                    "versionId": str(pipeline_versions.first().id),
                }
            },
        )
        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deletePipelineVersion"],
        )

    def test_add_pipeline_recipients(self):
        self.test_create_pipeline_version()
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()

        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        recipients {
                            user {
                                id
                            }
                        }
                    }
                  }
            }
        """,
            {
                "input": {
                    "id": str(pipeline.id),
                    "recipientIds": [str(self.USER_ROOT.id)],
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipeline": {"recipients": [{"user": {"id": str(self.USER_ROOT.id)}}]},
            },
            r["data"]["updatePipeline"],
        )

    def test_update_pipeline_recipients(self):
        self.test_create_pipeline_version()
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        PipelineRecipient.objects.create(pipeline=pipeline, user=self.USER_ROOT)
        PipelineRecipient.objects.create(pipeline=pipeline, user=self.USER_LAMBDA)

        self.assertEqual(pipeline.recipients.count(), 2)

        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        recipients {
                            user {
                                id
                            }
                        }
                    }
                  }
            }
        """,
            {
                "input": {
                    "id": str(pipeline.id),
                    "recipientIds": [
                        str(self.USER_LAMBDA.id),
                        str(self.USER_SABRINA.id),
                    ],
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipeline": {
                    "recipients": [
                        {"user": {"id": str(self.USER_SABRINA.id)}},
                        {"user": {"id": str(self.USER_LAMBDA.id)}},
                    ]
                },
            },
            r["data"]["updatePipeline"],
        )

    def test_update_pipeline_recipients_no_workspace_members(self):
        self.test_create_pipeline_version()
        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        r = self.run_query(
            """
            mutation updatePipeline($input: UpdatePipelineInput!) {
                updatePipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        recipients {
                            user {
                                id
                            }
                        }
                    }
                  }
            }
        """,
            {
                "input": {
                    "id": str(pipeline.id),
                    "recipientIds": [
                        str(self.USER_LAMBDA.id),
                        str(self.USER_NOOB.id),
                    ],
                }
            },
        )
        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "pipeline": {
                    "recipients": [
                        {"user": {"id": str(self.USER_LAMBDA.id)}},
                    ]
                },
            },
            r["data"]["updatePipeline"],
        )

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
        version = PipelineVersion.objects.get(pipeline=pipeline, number=1)
        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=version,
            trigger_mode=PipelineRunTrigger.MANUAL,
            config={},
            send_mail_notifications=True,
        )

        mail_run_recipients(run)
        self.assertEqual(
            f"Run report of {pipeline.code} ({run.state.label})",
            mail.outbox[0].subject,
        )
        self.assertListEqual([self.USER_ROOT.email], mail.outbox[0].recipients())
        self.assertTrue(
            f"https://{settings.NEW_FRONTEND_DOMAIN}/workspaces/{pipeline.workspace.slug}/pipelines/{pipeline.code}/runs/{run.id}"
            in mail.outbox[0].body
        )

    @test.override_settings(NEW_FRONT_DOMAIN="localhost:3000")
    def test_mail_run_recipients_scheduled_trigger(self):
        self.client.force_login(self.USER_ROOT)
        self.test_pipeline_new_run()

        pipeline = Pipeline.objects.filter_for_user(user=self.USER_ROOT).first()
        version = PipelineVersion.objects.get(pipeline=pipeline, number=1)
        PipelineRecipient.objects.create(pipeline=pipeline, user=self.USER_ROOT)
        PipelineRecipient.objects.create(pipeline=pipeline, user=self.USER_LAMBDA)

        run = pipeline.run(
            user=self.USER_ROOT,
            pipeline_version=version,
            trigger_mode=PipelineRunTrigger.SCHEDULED,
            config={},
            send_mail_notifications=True,
        )

        mail_run_recipients(run)
        self.assertEqual(
            f"Run report of {pipeline.code} ({run.state.label})",
            mail.outbox[0].subject,
        )
        self.assertListEqual(
            [self.USER_LAMBDA.email, self.USER_ROOT.email], mail.outbox[0].recipients()
        )
        self.assertTrue(
            f"https://{settings.NEW_FRONTEND_DOMAIN}/workspaces/{pipeline.workspace.slug}/pipelines/{pipeline.code}/runs/{run.id}"
            in mail.outbox[0].body
        )

    def test_pipeline_permission_schedule_true(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(self.USER_SABRINA).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
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

    def test_pipeline_permission_schedule_false(self):
        self.test_create_pipeline()
        self.client.force_login(self.USER_SABRINA)
        pipeline = Pipeline.objects.filter_for_user(self.USER_SABRINA).first()
        pipeline.upload_new_version(
            user=self.USER_ROOT,
            zipfile=base64.b64decode("".encode("ascii")),
            parameters={
                "code": "param1",
                "name": "Param 1",
                "type": "string",
                "help": "Param 1's Help",
                "default": "default value",
                "multiple": True,
                "required": True,
                "choices": ["Choice 1", "Choice 2"],
            },
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
                    "parameters": [
                        {
                            "code": "param1",
                            "name": "Param 1",
                            "type": "string",
                            "help": "Param 1's Help",
                            "default": "default value",
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
