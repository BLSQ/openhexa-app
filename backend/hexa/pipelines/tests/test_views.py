import asyncio
import base64
import json
import random
import string
import uuid
from unittest.mock import AsyncMock, patch
from urllib.parse import urlencode

from django.urls import reverse
from django.utils import timezone

from hexa.core.test import TestCase
from hexa.pipelines.models import (
    Pipeline,
    PipelineRun,
    PipelineRunState,
    PipelineRunTrigger,
    PipelineType,
)
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


def _parse_sse(content: bytes) -> list[dict]:
    events = []
    current: dict = {}
    for line in content.decode().splitlines():
        if line.startswith("event:"):
            current["event"] = line[len("event:") :].strip()
        elif line.startswith("data:"):
            current["data"] = json.loads(line[len("data:") :].strip())
        elif not line and current:
            events.append(current)
            current = {}
    return events


async def _collect_async_stream(streaming_content) -> bytes:
    chunks = []
    async for chunk in streaming_content:
        chunks.append(chunk)
    return b"".join(chunks)


class SSEStreamTest(TestCase):
    def setUp(self):
        super().setUp()
        patcher = patch("hexa.pipelines.views.connection.close")
        patcher.start()
        self.addCleanup(patcher.stop)

    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "sse_user@example.com", "password", is_superuser=True
        )
        cls.OTHER_USER = User.objects.create_user("sse_other@example.com", "password")

        cls.WORKSPACE = Workspace.objects.create_if_has_perm(
            cls.USER,
            name="SSE Test Workspace",
            description="",
        )
        cls.PIPELINE = Pipeline.objects.create(
            workspace=cls.WORKSPACE,
            name="SSE Test Pipeline",
            code="sse-test-pipeline",
        )

    def _make_run(self, state, messages=None):
        return PipelineRun.objects.create(
            pipeline=self.PIPELINE,
            user=self.USER,
            run_id="sse-test-run",
            execution_date=timezone.now(),
            trigger_mode=PipelineRunTrigger.MANUAL,
            state=state,
            messages=messages or [],
        )

    def _url(self, run_id):
        return reverse("pipelines:stream_pipeline_run_messages", args=[run_id])

    def _consume(self, response) -> list[dict]:
        content = asyncio.run(_collect_async_stream(response.streaming_content))
        return _parse_sse(content)

    # --- Auth / permission ---

    def test_unauthenticated_redirects_to_login(self):
        run = self._make_run(PipelineRunState.SUCCESS)
        response = self.client.get(self._url(run.id))
        self.assertEqual(response.status_code, 302)

    def test_run_not_found_returns_404(self):
        self.client.force_login(self.USER)
        response = self.client.get(self._url(uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_access_run(self):
        run = self._make_run(PipelineRunState.SUCCESS)
        self.client.force_login(self.OTHER_USER)
        response = self.client.get(self._url(run.id))
        self.assertEqual(response.status_code, 404)

    # --- Terminal run (finished before stream opens) ---

    def test_terminal_run_no_messages_sends_done(self):
        run = self._make_run(PipelineRunState.SUCCESS, messages=[])
        self.client.force_login(self.USER)
        response = self.client.get(self._url(run.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/event-stream")
        self.assertEqual(response["Cache-Control"], "no-cache")
        events = self._consume(response)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "done")
        self.assertEqual(events[0]["data"]["status"], PipelineRunState.SUCCESS)

    def test_terminal_run_with_messages_sends_messages_then_done(self):
        messages = [
            {"message": "Starting", "timestamp": None, "priority": "INFO"},
            {"message": "Finished", "timestamp": None, "priority": "INFO"},
        ]
        run = self._make_run(PipelineRunState.SUCCESS, messages=messages)
        self.client.force_login(self.USER)
        response = self.client.get(self._url(run.id))
        events = self._consume(response)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]["event"], "message")
        self.assertEqual(events[0]["data"]["message"], "Starting")
        self.assertEqual(events[1]["event"], "message")
        self.assertEqual(events[1]["data"]["message"], "Finished")
        self.assertEqual(events[2]["event"], "done")

    def test_terminal_run_cursor_skips_seen_messages(self):
        messages = [
            {"message": "First", "timestamp": None, "priority": "INFO"},
            {"message": "Second", "timestamp": None, "priority": "INFO"},
        ]
        run = self._make_run(PipelineRunState.SUCCESS, messages=messages)
        self.client.force_login(self.USER)
        response = self.client.get(self._url(run.id) + "?from=1")
        events = self._consume(response)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["data"]["message"], "Second")
        self.assertEqual(events[1]["event"], "done")

    def test_terminal_run_invalid_cursor_defaults_to_zero(self):
        run = self._make_run(PipelineRunState.SUCCESS, messages=[])
        self.client.force_login(self.USER)
        response = self.client.get(self._url(run.id) + "?from=notanumber")
        self.assertEqual(response.status_code, 200)
        events = self._consume(response)
        self.assertEqual(events[-1]["event"], "done")

    # --- Running run (transitions to terminal while streaming) ---

    def test_running_run_transitions_and_sends_done(self):
        run = self._make_run(
            PipelineRunState.RUNNING,
            messages=[{"message": "Hello", "timestamp": None, "priority": "INFO"}],
        )
        self.client.force_login(self.USER)

        call_count = 0

        def on_get():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                run.state = PipelineRunState.SUCCESS

        with (
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch(
                "hexa.pipelines.views.PipelineRun.objects.filter_for_user",
                return_value=_MockQuerySet(run, on_get=on_get),
            ),
        ):
            response = self.client.get(self._url(run.id))
            events = self._consume(response)

        message_events = [e for e in events if e["event"] == "message"]
        done_events = [e for e in events if e["event"] == "done"]
        self.assertEqual(len(message_events), 1)
        self.assertEqual(message_events[0]["data"]["message"], "Hello")
        self.assertEqual(len(done_events), 1)

    def test_running_run_sends_timeout_when_max_duration_exceeded(self):
        run = self._make_run(PipelineRunState.RUNNING, messages=[])
        self.client.force_login(self.USER)

        with (
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("hexa.pipelines.views.MAX_DURATION", 0),
            patch(
                "hexa.pipelines.views.PipelineRun.objects.filter_for_user",
                return_value=_MockQuerySet(run),
            ),
        ):
            response = self.client.get(self._url(run.id))
            events = self._consume(response)

        self.assertEqual(events[-1]["event"], "timeout")


class _MockQuerySet:
    """Minimal queryset stub that returns a fixed run for .get()."""

    def __init__(self, run, on_get=None):
        self._run = run
        self._on_get = on_get

    def only(self, *fields):
        return self

    def get(self, id):
        if str(self._run.id) == str(id):
            if self._on_get:
                self._on_get()
            return self._run
        raise PipelineRun.DoesNotExist
