"""OpenHEXA as the OpenTelemetry collector of its notebook servers.

The AI tooling of a notebook server (Jupyternaut, through litellm) exports
OTLP/HTTP traces to /notebooks/telemetry/v1/traces, authenticated with the
workspace token the server holds (openhexa-docker-images: hexa-ai-env.sh and
the hexa_ai_telemetry server extension). Of each model call, we keep the token
usage as an `AiUsage` row, priced like the app's own agents' usage, so that it
counts towards the organization's monthly AI budget; and we forward the payload
to Logfire under our own token, with the identities we know stamped on its
resource. The notebook servers never hold a Logfire token.

Payloads are protobuf, the encoding the exporters we configure use; OTLP/JSON
is not accepted.
"""

import gzip
import logging
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime

import requests
from django.utils import timezone
from google.protobuf.message import DecodeError, Message
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
    ExportLogsServiceRequest,
)
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import (
    ExportMetricsServiceRequest,
)
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
)
from opentelemetry.proto.common.v1.common_pb2 import AnyValue, KeyValue
from pydantic_ai import RunUsage

from hexa.assistant.ai_models.backends import backend_for
from hexa.assistant.ai_models.built_model import price_usage
from hexa.assistant.ai_models.ids import ModelId
from hexa.assistant.models import AiUsage
from hexa.user_management.models import AiSettings, Organization, User
from hexa.workspaces.models import Workspace

logger = logging.getLogger(__name__)

PROTOBUF_CONTENT_TYPE = "application/x-protobuf"

SIGNALS: dict[str, type[Message]] = {
    "traces": ExportTraceServiceRequest,
    "logs": ExportLogsServiceRequest,
    "metrics": ExportMetricsServiceRequest,
}

# What litellm calls the provider (gen_ai.system) each of our providers reaches.
# A call to any other provider was made with the user's own key, not ours.
LITELLM_PROVIDERS = {
    AiSettings.Provider.MANAGED: "vertex_ai",
    AiSettings.Provider.ANTHROPIC: "anthropic",
}
# Attributes litellm's exporter puts on a model call; the cache ones are added
# by our server extension, under the names pydantic-ai and Logfire use.
INPUT_TOKENS = "gen_ai.usage.input_tokens"
OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
CACHE_READ_TOKENS = "gen_ai.usage.cache_read.input_tokens"
CACHE_WRITE_TOKENS = "gen_ai.usage.cache_creation.input_tokens"

DEFAULT_LOGFIRE_BASE_URL = "https://logfire-us.pydantic.dev"
LOGFIRE_TIMEOUT_SECONDS = 10


class TelemetryError(ValueError):
    """The request is not something we can read."""


def parse_request(
    signal: str,
    body: bytes,
    *,
    content_type: str | None,
    content_encoding: str | None = None,
) -> Message:
    """The OTLP export request in `body`, or raise `TelemetryError`."""
    try:
        message_type = SIGNALS[signal]
    except KeyError:
        raise TelemetryError(f"Unknown signal {signal!r}") from None
    if not (content_type or "").startswith(PROTOBUF_CONTENT_TYPE):
        raise TelemetryError(
            f"Unsupported Content-Type {content_type!r}; send {PROTOBUF_CONTENT_TYPE}"
        )
    if content_encoding == "gzip":
        try:
            body = gzip.decompress(body)
        except (OSError, EOFError) as e:
            raise TelemetryError("Invalid gzip payload") from e
    elif content_encoding:
        raise TelemetryError(f"Unsupported Content-Encoding {content_encoding!r}")
    message = message_type()
    try:
        message.ParseFromString(body)
    except DecodeError as e:
        raise TelemetryError("Invalid protobuf payload") from e
    return message


def _attribute_value(value: AnyValue):
    kind = value.WhichOneof("value")
    return getattr(value, kind) if kind else None


def _attributes(key_values) -> dict:
    return {kv.key: _attribute_value(kv.value) for kv in key_values}


def _int(value) -> int:
    try:
        return max(int(value or 0), 0)
    except (TypeError, ValueError):
        return 0


@dataclass(frozen=True)
class ReportedUsage:
    """The usage of one model call, as a span reports it."""

    source: str
    provider: str
    model: str
    input_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    output_tokens: int
    occurred_at: datetime
    external_id: str | None

    @property
    def run_usage(self) -> RunUsage:
        return RunUsage(
            input_tokens=self.input_tokens,
            cache_read_tokens=self.cache_read_tokens,
            cache_write_tokens=self.cache_write_tokens,
            output_tokens=self.output_tokens,
        )


def reported_usages(request: ExportTraceServiceRequest) -> list[ReportedUsage]:
    """The model calls in a trace export: the spans that carry a token usage."""
    usages = []
    for resource_spans in request.resource_spans:
        resource = _attributes(resource_spans.resource.attributes)
        source = str(resource.get("service.name") or "unknown")
        for scope_spans in resource_spans.scope_spans:
            for span in scope_spans.spans:
                attributes = _attributes(span.attributes)
                if INPUT_TOKENS not in attributes and OUTPUT_TOKENS not in attributes:
                    continue
                model = attributes.get("gen_ai.request.model") or attributes.get(
                    "gen_ai.response.model"
                )
                if not model:
                    continue
                if span.end_time_unix_nano:
                    occurred_at = datetime.fromtimestamp(
                        span.end_time_unix_nano / 1e9, tz=UTC
                    )
                else:
                    occurred_at = timezone.now()
                external_id = (
                    attributes.get("litellm.call_id")
                    or attributes.get("gen_ai.response.id")
                    or span.span_id.hex()
                    or None
                )
                usages.append(
                    ReportedUsage(
                        source=source,
                        provider=str(attributes.get("gen_ai.system") or ""),
                        model=str(model),
                        input_tokens=_int(attributes.get(INPUT_TOKENS)),
                        cache_read_tokens=_int(attributes.get(CACHE_READ_TOKENS)),
                        cache_write_tokens=_int(attributes.get(CACHE_WRITE_TOKENS)),
                        output_tokens=_int(attributes.get(OUTPUT_TOKENS)),
                        occurred_at=occurred_at,
                        external_id=str(external_id) if external_id else None,
                    )
                )
    return usages


def record_usage(
    request: ExportTraceServiceRequest,
    *,
    organization: Organization,
    workspace: Workspace,
    user: User,
) -> list[AiUsage]:
    """Charge the model calls in `request` made on the organization's
    credentials to the organization. Calls to other providers (the user's own
    keys) are left out, as is everything when its assistant is off.
    """
    ai_settings = organization.ai_settings_safe
    if not ai_settings.enabled:
        return []
    provider = LITELLM_PROVIDERS.get(ai_settings.provider)
    backend = backend_for(ai_settings)

    rows = []
    for usage in reported_usages(request):
        if usage.provider != provider:
            continue
        # Claude is all the notebooks are given, and priced per the backend.
        model_id = ModelId(provider="anthropic", name=usage.model)
        cost = price_usage(
            usage.run_usage,
            usage.model,
            backend.pricing_provider(model_id),
            backend.price_override(model_id),
        )
        rows.append(
            AiUsage(
                organization=organization,
                workspace=workspace,
                user=user,
                source=usage.source[:50],
                model=usage.model[:100],
                input_tokens=usage.input_tokens,
                cache_read_tokens=usage.cache_read_tokens,
                cache_write_tokens=usage.cache_write_tokens,
                output_tokens=usage.output_tokens,
                cost=cost,
                occurred_at=usage.occurred_at,
                external_id=usage.external_id[:200] if usage.external_id else None,
            )
        )
    if not rows:
        return []
    # A delivery the exporter retried brings calls we already have: skip them.
    return AiUsage.objects.bulk_create(rows, ignore_conflicts=True)


def stamp_identity(
    message: Message,
    *,
    organization: Organization,
    workspace: Workspace,
    user: User,
    environment: str | None = None,
) -> None:
    """Put the identities we know on every resource of `message`, replacing
    whatever the container claimed.
    """
    attributes = {
        "hexa.organization": organization.slug,
        "hexa.workspace": workspace.slug,
        "hexa.user": user.email,
    }
    environment = environment or os.environ.get("SENTRY_ENVIRONMENT")
    if environment:
        # The attribute Logfire builds its environment filter on.
        attributes["deployment.environment.name"] = environment

    # ExportTraceServiceRequest.resource_spans, ExportLogsServiceRequest.resource_logs...
    (resources_field,) = message.DESCRIPTOR.fields
    for entry in getattr(message, resources_field.name):
        kept = [
            KeyValue(key=kv.key, value=kv.value)
            for kv in entry.resource.attributes
            if kv.key not in attributes
        ]
        del entry.resource.attributes[:]
        entry.resource.attributes.extend(kept)
        for key, value in attributes.items():
            entry.resource.attributes.add(key=key, value=AnyValue(string_value=value))


@dataclass(frozen=True)
class LogfireTarget:
    base_url: str
    token: str

    def url(self, signal: str) -> str:
        return f"{self.base_url}/v1/{signal}"


def logfire_target() -> LogfireTarget | None:
    """Where to forward the telemetry, if Logfire is on (same switches as the
    assistant's own instrumentation in hexa.assistant.apps).
    """
    if os.environ.get("LOGFIRE_SEND_TO_LOGFIRE", "false").lower() != "true":
        return None
    token = (os.environ.get("LOGFIRE_TOKEN") or "").strip().strip("\"'")
    if not token:
        return None
    base_url = os.environ.get("LOGFIRE_BASE_URL")
    if not base_url:
        # The region is in the token: pylf_v1_eu_..., see config/settings/eval.py.
        match = re.match(r"^pylf_v\d+_(?P<region>[a-z]{2})_", token)
        base_url = (
            f"https://logfire-{match['region']}.pydantic.dev"
            if match
            else DEFAULT_LOGFIRE_BASE_URL
        )
    return LogfireTarget(base_url=base_url.rstrip("/"), token=token)


def forward_to_logfire(signal: str, payload: bytes, target: LogfireTarget) -> bool:
    """Send an OTLP payload on to Logfire. Failures are logged, not raised:
    the notebook already did its part.
    """
    try:
        response = requests.post(
            target.url(signal),
            data=payload,
            headers={
                "Authorization": target.token,
                "Content-Type": PROTOBUF_CONTENT_TYPE,
            },
            timeout=LOGFIRE_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.warning(
            "Could not forward %s telemetry to Logfire", signal, exc_info=True
        )
        return False
    return True
