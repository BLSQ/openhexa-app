"""The telemetry endpoint of the notebook servers: usage accounting and
forwarding to Logfire. Payloads are built the way litellm's OpenTelemetry
exporter, as configured in the notebook images, builds them.
"""

import os
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import patch

import genai_prices
from genai_prices.types import Usage
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
)

from hexa.assistant import telemetry
from hexa.assistant.models import AiUsage
from hexa.core.test import TestCase
from hexa.user_management.models import AiSettings, User
from hexa.workspaces.authentication import WorkspaceToken
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

PROTOBUF = "application/x-protobuf"
OCCURRED_AT = datetime(2026, 10, 16, 12, 30, tzinfo=UTC)


def _set_attributes(key_values, attributes: dict):
    for key, value in attributes.items():
        kv = key_values.add()
        kv.key = key
        if isinstance(value, bool):
            kv.value.bool_value = value
        elif isinstance(value, int):
            kv.value.int_value = value
        elif isinstance(value, float):
            kv.value.double_value = value
        else:
            kv.value.string_value = value


def trace_request(
    *,
    source="jupyternaut",
    provider="vertex_ai",
    model="claude-opus-4-6",
    input_tokens=1000,
    cache_read=600,
    cache_write=100,
    output_tokens=20,
    call_id="call-1",
    with_usage=True,
) -> ExportTraceServiceRequest:
    request = ExportTraceServiceRequest()
    resource_spans = request.resource_spans.add()
    _set_attributes(
        resource_spans.resource.attributes,
        {"service.name": source, "hexa.workspace": "claimed-by-the-container"},
    )
    span = resource_spans.scope_spans.add().spans.add()
    span.name = "litellm_request"
    span.trace_id = bytes(range(16))
    span.span_id = bytes(range(8))
    span.end_time_unix_nano = int(OCCURRED_AT.timestamp() * 1e9)
    attributes = {
        "gen_ai.system": provider,
        "gen_ai.request.model": model,
        "litellm.call_id": call_id,
    }
    if with_usage:
        attributes.update(
            {
                "gen_ai.usage.input_tokens": input_tokens,
                "gen_ai.usage.output_tokens": output_tokens,
                "gen_ai.usage.total_tokens": input_tokens + output_tokens,
                "gen_ai.usage.cache_read.input_tokens": cache_read,
                "gen_ai.usage.cache_creation.input_tokens": cache_write,
            }
        )
    _set_attributes(span.attributes, attributes)
    return request


def _resource_attributes(payload: bytes) -> dict:
    request = ExportTraceServiceRequest()
    request.ParseFromString(payload)
    (resource_spans,) = request.resource_spans
    return {kv.key: kv.value.string_value for kv in resource_spans.resource.attributes}


class TelemetryViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("jane@bluesquarehub.com", "janerocks2")
        cls.WORKSPACE = create_workspace(name="Telemetry Workspace")
        cls.ORGANIZATION = cls.WORKSPACE.organization
        AiSettings.objects.update_or_create(
            organization=cls.ORGANIZATION,
            defaults={"enabled": True, "provider": AiSettings.Provider.MANAGED},
        )
        membership = WorkspaceMembership.objects.create(
            workspace=cls.WORKSPACE, user=cls.USER, role=WorkspaceMembershipRole.ADMIN
        )
        cls.TOKEN = WorkspaceToken.issue(
            user=cls.USER, workspace=cls.WORKSPACE, membership=membership
        ).sign()

    def post(self, signal, request, *, token=None, bearer=False, **extra):
        authorization = token if token is not None else self.TOKEN
        if bearer:
            authorization = f"Bearer {authorization}"
        return self.client.post(
            f"/notebooks/telemetry/v1/{signal}",
            data=request.SerializeToString(),
            content_type=PROTOBUF,
            HTTP_AUTHORIZATION=authorization,
            **extra,
        )

    def test_records_the_usage_of_a_model_call(self):
        response = self.post("traces", trace_request())

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response["Content-Type"], PROTOBUF)
        usage = AiUsage.objects.get()
        self.assertEqual(usage.organization, self.ORGANIZATION)
        self.assertEqual(usage.workspace, self.WORKSPACE)
        self.assertEqual(usage.user, self.USER)
        self.assertEqual(usage.source, "jupyternaut")
        self.assertEqual(usage.model, "claude-opus-4-6")
        self.assertEqual(
            (
                usage.input_tokens,
                usage.cache_read_tokens,
                usage.cache_write_tokens,
                usage.output_tokens,
            ),
            (1000, 600, 100, 20),
        )
        self.assertEqual(usage.occurred_at, OCCURRED_AT)
        self.assertEqual(usage.external_id, "call-1")
        # Priced as the managed backend prices the app's own agents.
        expected = genai_prices.calc_price(
            Usage(
                input_tokens=1000,
                cache_read_tokens=600,
                cache_write_tokens=100,
                output_tokens=20,
            ),
            "claude-opus-4-6",
            provider_id="google-vertex",
        ).total_price
        self.assertGreater(expected, 0)
        self.assertEqual(usage.cost, Decimal(expected).quantize(Decimal("0.000001")))

    def test_counts_towards_the_organization_monthly_cost(self):
        with patch("django.utils.timezone.now", return_value=OCCURRED_AT):
            self.post("traces", trace_request(call_id="a"))
            self.post("traces", trace_request(call_id="b"))
            cost = self.ORGANIZATION.get_monthly_ai_cost()
        total = sum(usage.cost for usage in AiUsage.objects.all())
        self.assertEqual(AiUsage.objects.count(), 2)
        self.assertEqual(cost, float(round(total, 2)))

    def test_a_retried_delivery_is_not_counted_twice(self):
        self.post("traces", trace_request(call_id="same"))
        self.post("traces", trace_request(call_id="same"))
        self.assertEqual(AiUsage.objects.count(), 1)

    def test_a_bearer_header_is_accepted_too(self):
        response = self.post("traces", trace_request(), bearer=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AiUsage.objects.count(), 1)

    def test_calls_to_other_providers_are_not_charged(self):
        """A model the user reached with their own key, added in Jupyternaut's
        settings, is not the organization's expense.
        """
        response = self.post("traces", trace_request(provider="openai", model="gpt-5"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AiUsage.objects.count(), 0)

    def test_byok_organizations_pay_anthropic_prices(self):
        AiSettings.objects.filter(organization=self.ORGANIZATION).update(
            provider=AiSettings.Provider.ANTHROPIC,
            model=AiSettings.Model.SONNET,
            api_key="sk-ant-test",
        )
        self.post(
            "traces", trace_request(provider="anthropic", model="claude-sonnet-4-6")
        )
        usage = AiUsage.objects.get()
        expected = genai_prices.calc_price(
            Usage(
                input_tokens=1000,
                cache_read_tokens=600,
                cache_write_tokens=100,
                output_tokens=20,
            ),
            "claude-sonnet-4-6",
            provider_id="anthropic",
        ).total_price
        self.assertEqual(usage.cost, Decimal(expected).quantize(Decimal("0.000001")))
        # The Vertex calls of a managed set-up would not be this organization's.
        self.post("traces", trace_request(provider="vertex_ai", call_id="other"))
        self.assertEqual(AiUsage.objects.count(), 1)

    def test_nothing_is_charged_when_the_assistant_is_off(self):
        AiSettings.objects.filter(organization=self.ORGANIZATION).update(enabled=False)
        response = self.post("traces", trace_request())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AiUsage.objects.count(), 0)

    def test_spans_without_usage_are_ignored(self):
        self.post("traces", trace_request(with_usage=False))
        self.assertEqual(AiUsage.objects.count(), 0)

    def test_an_unknown_model_price_is_recorded_without_cost(self):
        self.post("traces", trace_request(model="claude-unknown-9"))
        usage = AiUsage.objects.get()
        self.assertIsNone(usage.cost)
        self.assertEqual(usage.input_tokens, 1000)

    def test_rejects_an_invalid_token(self):
        response = self.post("traces", trace_request(), token="not-a-token")
        self.assertEqual(response.status_code, 401)
        response = self.post("traces", trace_request(), token="")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(AiUsage.objects.count(), 0)

    def test_rejects_an_unknown_signal(self):
        response = self.post("profiles", trace_request())
        self.assertEqual(response.status_code, 404)

    def test_rejects_what_is_not_protobuf(self):
        response = self.client.post(
            "/notebooks/telemetry/v1/traces",
            data=b"{}",
            content_type="application/json",
            HTTP_AUTHORIZATION=self.TOKEN,
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            "/notebooks/telemetry/v1/traces",
            data=b"\xff\xff\xff",
            content_type=PROTOBUF,
            HTTP_AUTHORIZATION=self.TOKEN,
        )
        self.assertEqual(response.status_code, 400)

    def test_other_signals_are_accepted_without_accounting(self):
        from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
            ExportLogsServiceRequest,
        )

        request = ExportLogsServiceRequest()
        _set_attributes(
            request.resource_logs.add().resource.attributes,
            {"service.name": "jupyternaut"},
        )
        response = self.post("logs", request)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(AiUsage.objects.count(), 0)

    @patch("hexa.assistant.telemetry.requests.post")
    def test_not_forwarded_when_logfire_is_off(self, post):
        with patch.dict(os.environ, {"LOGFIRE_SEND_TO_LOGFIRE": "false"}):
            self.post("traces", trace_request())
        post.assert_not_called()

    @patch("hexa.assistant.telemetry.requests.post")
    def test_forwarded_to_logfire_with_the_identities_we_know(self, post):
        environment = {
            "LOGFIRE_SEND_TO_LOGFIRE": "true",
            "LOGFIRE_TOKEN": "pylf_v1_eu_testtoken",
            "SENTRY_ENVIRONMENT": "test",
        }
        with patch.dict(os.environ, environment):
            os.environ.pop("LOGFIRE_BASE_URL", None)
            response = self.post("traces", trace_request())

        self.assertEqual(response.status_code, 200)
        post.assert_called_once()
        (url,), kwargs = post.call_args
        self.assertEqual(url, "https://logfire-eu.pydantic.dev/v1/traces")
        self.assertEqual(kwargs["headers"]["Authorization"], "pylf_v1_eu_testtoken")
        self.assertEqual(kwargs["headers"]["Content-Type"], PROTOBUF)
        resource = _resource_attributes(kwargs["data"])
        self.assertEqual(resource["service.name"], "jupyternaut")
        self.assertEqual(resource["hexa.organization"], self.ORGANIZATION.slug)
        self.assertEqual(resource["hexa.workspace"], self.WORKSPACE.slug)
        self.assertEqual(resource["hexa.user"], self.USER.email)
        self.assertEqual(resource["deployment.environment.name"], "test")

    @patch("hexa.assistant.telemetry.requests.post", side_effect=OSError("down"))
    def test_a_logfire_outage_does_not_fail_the_delivery(self, post):
        import requests

        post.side_effect = requests.ConnectionError("down")
        environment = {
            "LOGFIRE_SEND_TO_LOGFIRE": "true",
            "LOGFIRE_TOKEN": "pylf_v1_us_x",
        }
        with patch.dict(os.environ, environment):
            response = self.post("traces", trace_request())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AiUsage.objects.count(), 1)


class LogfireTargetTest(TestCase):
    def test_region_from_token(self):
        with patch.dict(
            os.environ,
            {"LOGFIRE_SEND_TO_LOGFIRE": "true", "LOGFIRE_TOKEN": "pylf_v1_eu_abc"},
        ):
            os.environ.pop("LOGFIRE_BASE_URL", None)
            target = telemetry.logfire_target()
        self.assertEqual(target.base_url, "https://logfire-eu.pydantic.dev")
        self.assertEqual(target.url("logs"), "https://logfire-eu.pydantic.dev/v1/logs")

    def test_explicit_base_url(self):
        with patch.dict(
            os.environ,
            {
                "LOGFIRE_SEND_TO_LOGFIRE": "true",
                "LOGFIRE_TOKEN": "whatever",
                "LOGFIRE_BASE_URL": "https://logfire.example.org/",
            },
        ):
            target = telemetry.logfire_target()
        self.assertEqual(target.base_url, "https://logfire.example.org")

    def test_off_without_token(self):
        with patch.dict(
            os.environ, {"LOGFIRE_SEND_TO_LOGFIRE": "true", "LOGFIRE_TOKEN": ""}
        ):
            self.assertIsNone(telemetry.logfire_target())
