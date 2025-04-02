import base64
import random
import string
import uuid
from unittest.mock import patch
from urllib.parse import urlencode

from django.urls import reverse

from hexa.core.test import TestCase
from hexa.pipelines.models import Pipeline, PipelineRunTrigger, PipelineType
from hexa.user_management.models import User
from hexa.workspaces.models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_JANE = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks2",
        )

        cls.USER_JULIA = User.objects.create_user(
            "julia@bluesquarehub.com",
            "juliaspassword",
        )

        cls.USER_SUPERUSER = User.objects.create_user(
            "rebecca@bluesquarehub.com", "standardpassword", is_superuser=True
        )

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER_SUPERUSER,
            name="Senegal Workspace",
            description="This is a workspace for Senegal",
        )

        cls.WORKSPACE_MEMBERSHIP_SUPERUSER = WorkspaceMembership.objects.get(
            workspace=cls.WORKSPACE, user=cls.USER_SUPERUSER
        )

        cls.WORKSPACE_MEMBERSHIP_JULIA = WorkspaceMembership.objects.create(
            user=cls.USER_JULIA,
            workspace=cls.WORKSPACE,
            role=WorkspaceMembershipRole.ADMIN,
        )

        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="Test pipeline",
            code="my-pipeline",
            description="This is a test pipeline",
            webhook_enabled=True,
        )
        cls.PIPELINE.generate_webhook_token()
        cls.PIPELINE.upload_new_version(
            cls.USER_JULIA, zipfile=b"", name="Version 1", parameters=[]
        )

    def test_run_pipeline_invalid_token(self):
        token = base64.b64encode(
            "".join(random.choices(string.ascii_lowercase, k=10)).encode("utf-8")
        ).decode()
        r = self.client.post(
            reverse(
                "pipelines:run",
                args=[token],
            ),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), {"error": "Invalid token"})

    def test_run_pipeline_not_enabled(self):
        self.PIPELINE.webhook_enabled = False
        self.PIPELINE.save()
        r = self.client.post(
            reverse(
                "pipelines:run",
                args=[self.PIPELINE.webhook_token],
            ),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), {"error": "Pipeline has no webhook enabled"})

    def test_run_pipeline_notebook_webhook(self):
        pipeline = Pipeline.objects.create(
            code="new_pipeline",
            name="notebook.ipynb",
            workspace=self.WORKSPACE,
            type=PipelineType.NOTEBOOK,
            notebook_path="notebook.ipynb",
            webhook_enabled=True,
        )
        pipeline.generate_webhook_token()

        response = self.client.post(
            reverse(
                "pipelines:run",
                args=[pipeline.webhook_token],
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(pipeline.last_run.id), response.json()["run_id"])
        self.assertEqual(pipeline.last_run.trigger_mode, PipelineRunTrigger.WEBHOOK)

    def test_run_pipeline_valid(self):
        self.assertEqual(self.PIPELINE.last_run, None)
        response = self.client.post(
            reverse(
                "pipelines:run",
                args=[self.PIPELINE.webhook_token],
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(self.PIPELINE.last_run.id), response.json()["run_id"])
        self.assertEqual(
            self.PIPELINE.last_run.trigger_mode, PipelineRunTrigger.WEBHOOK
        )

    def test_run_pipeline_old_token(self):
        self.assertEqual(self.PIPELINE.last_run, None)
        old_token = self.PIPELINE.webhook_token

        with patch("hexa.pipelines.models.TimestampSigner") as mocked_signer:
            random_string = base64.b64encode(
                "".join(random.choices(string.ascii_lowercase, k=10)).encode("utf-8")
            ).decode()

            signer = mocked_signer.return_value
            signer.sign.return_value = base64.b64encode(
                random_string.encode("utf-8")
            ).decode()

            self.PIPELINE.generate_webhook_token()
            self.PIPELINE.refresh_from_db()

            response = self.client.post(
                reverse(
                    "pipelines:run",
                    args=[old_token],
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {"error": "Pipeline not found"})

    def test_run_pipeline_specific_version(self):
        response = self.client.post(
            reverse(
                "pipelines:run_with_version",
                args=[self.PIPELINE.webhook_token, self.PIPELINE.last_version.id],
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.PIPELINE.last_run.pipeline_version, self.PIPELINE.last_version
        )

    def test_run_pipeline_invalid_version(self):
        self.assertEqual(self.PIPELINE.last_run, None)
        response = self.client.post(
            reverse(
                "pipelines:run_with_version",
                args=[self.PIPELINE.webhook_token, uuid.uuid4()],
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Pipeline version not found"})

    def test_run_pipeline_with_multiple_config(self):
        self.assert200withConfig(
            [
                {
                    "code": "my_parameter",
                    "name": "My parameter",
                    "type": "int",
                    "required": False,
                    "multiple": True,
                }
            ],
            {},
            {},
        )
        self.assert200withConfig(
            [
                {
                    "code": "my_parameter",
                    "name": "My parameter",
                    "type": "int",
                    "required": False,
                    "multiple": True,
                }
            ],
            {"param": [1, 2]},
            {"param": [1, 2]},
        )

    def assert200withConfig(
        self,
        parameters,
        config,
        result_config,
        content_type="application/json",
    ):
        self.PIPELINE.upload_new_version(
            self.USER_JULIA,
            parameters,
            zipfile=b"",
            name=str(uuid.uuid4()),
        )
        endpoint_url = reverse(
            "pipelines:run",
            args=[self.PIPELINE.webhook_token],
        )
        r = self.client.post(
            endpoint_url,
            content_type=content_type,
            data=(
                config
                if "application/json" == content_type
                else urlencode(config, doseq=True)
            ),
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.config, result_config)

    def test_run_multiple_form_urlencoded(self):
        self.assert200withConfig(
            [
                {
                    "code": "my_parameter",
                    "name": "My parameter",
                    "type": "string",
                    "required": True,
                    "multiple": True,
                }
            ],
            {"my_parameter": ["foo", "bar"]},
            {"my_parameter": ["foo", "bar"]},
        )

    def test_urlencoded_int_parameter(self):
        # Empty value
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "int",
                    "required": False,
                }
            ],
            {"send_mail_notifications": True, "log_level": "INFO"},
            {},
            content_type="application/x-www-form-urlencoded",
        )

        # Single value
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "int",
                    "required": True,
                }
            ],
            {"param": 1},
            {"param": 1},
            content_type="application/x-www-form-urlencoded",
        )

        # Multiple
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "int",
                    "multiple": True,
                }
            ],
            {"param": [1, 2]},
            {"param": [1, 2]},
            content_type="application/x-www-form-urlencoded",
        )

        # Multiple with empty value
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "int",
                    "multiple": True,
                }
            ],
            {"send_mail_notifications": "1"},
            {},
            content_type="application/x-www-form-urlencoded",
        )

    def test_urlencoded_default_parameter(self):
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "string",
                    "required": False,
                    "default": "foo",
                }
            ],
            {"send_mail_notifications": "1"},
            {"param": "foo"},
            content_type="application/x-www-form-urlencoded",
        )

    def test_urlencoded_float_parameter(self):
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "float",
                    "required": True,
                }
            ],
            {"param": 1.5},
            {"param": 1.5},
            content_type="application/x-www-form-urlencoded",
        )

        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "float",
                    "multiple": True,
                }
            ],
            {"param": [1.5, 2.5]},
            {"param": [1.5, 2.5]},
            content_type="application/x-www-form-urlencoded",
        )

    def test_urlencoded_boolean_parameter(self):
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "bool",
                    "required": True,
                }
            ],
            {"param": "true"},
            {"param": True},
            content_type="application/x-www-form-urlencoded",
        )
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "bool",
                    "required": True,
                }
            ],
            {"param": 1},
            {"param": True},
            content_type="application/x-www-form-urlencoded",
        )

        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "bool",
                }
            ],
            {"param": "false"},
            {"param": False},
            content_type="application/x-www-form-urlencoded",
        )
        self.assert200withConfig(
            [
                {
                    "code": "param",
                    "name": "Param",
                    "type": "bool",
                }
            ],
            {"param": 0},
            {"param": False},
            content_type="application/x-www-form-urlencoded",
        )

    def test_send_mail_notifications(self):
        endpoint_url = reverse(
            "pipelines:run",
            args=[self.PIPELINE.webhook_token],
        )
        r = self.client.post(
            endpoint_url,
            data=urlencode({"send_mail_notifications": True}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.send_mail_notifications, True)

        r = self.client.post(
            endpoint_url,
            data=urlencode({"send_mail_notifications": False}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.send_mail_notifications, False)

        r = self.client.post(
            endpoint_url,
            data=urlencode({"send_mail_notifications": 0}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.send_mail_notifications, False)

        # And in application/json
        r = self.client.post(
            endpoint_url + "?send_mail_notifications=1",
            data={},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.PIPELINE.last_run.send_mail_notifications, True)
