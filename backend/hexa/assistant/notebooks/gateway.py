"""An OpenAI-compatible chat completions API in front of the organization's model.

The AI tooling of notebook servers (Jupyternaut, through litellm) calls
POST /assistant/gateway/v1/chat/completions the way it would call OpenAI,
authenticated with its workspace token. The request runs here, on the model the
organization's backend selects for the "notebooks" agent key, whatever its
provider: Claude or Gemini on our Vertex project, the organization's own
Anthropic key, an OpenAI-compatible endpoint... So the credentials never leave
the app, every call is traced like the agents' own, and its usage is charged to
the organization's monthly AI budget before the response goes out.

Implements the part of the Chat Completions API the tooling uses: text and
image input, function tools, streaming and non-streaming responses. Requests
are translated to pydantic-ai messages and the model's response back.
"""

import base64
import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import messages as ai
from pydantic_ai.models import ModelRequestParameters
from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.models.instrumented import InstrumentedModel
from pydantic_ai.settings import ModelSettings
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.usage import RequestUsage

from hexa.assistant.ai_models.built_model import BuiltModel

logger = logging.getLogger(__name__)

DEFAULT_MAX_TOKENS = 8192
DEFAULT_TOOL_PARAMETERS = {"type": "object", "properties": {}}
# pydantic-ai's finish reasons -> the Chat Completions API's.
FINISH_REASONS = {
    "stop": "stop",
    "length": "length",
    "content_filter": "content_filter",
    "tool_call": "tool_calls",
    "error": "stop",
}


class GatewayError(ValueError):
    """The request is not a chat completion we can run."""


# ---------------------------------------------------------------------------
# Request: Chat Completions -> pydantic-ai
# ---------------------------------------------------------------------------


@dataclass
class ChatRequest:
    messages: list[ai.ModelMessage]
    tools: list[ToolDefinition] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
    stream: bool = False
    include_usage: bool = False
    # What the client asked for; informational, the organization's model runs.
    requested_model: str = ""

    @property
    def request_parameters(self) -> ModelRequestParameters:
        return ModelRequestParameters(function_tools=self.tools, allow_text_output=True)

    def model_settings(self, max_tokens: int = DEFAULT_MAX_TOKENS) -> ModelSettings:
        # Prompt caching for Claude, like the agents; other providers ignore the
        # anthropic_* keys (Gemini caches prompt prefixes implicitly).
        return AnthropicModelSettings(
            anthropic_cache_instructions=True,
            anthropic_cache_tool_definitions=True,
            anthropic_cache=True,
            **{"max_tokens": max_tokens, **self.settings},
        )


def _text(content: Any) -> str:
    """The text of a message content that may be a string or content parts."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return str(content)


def _image(image_url: Any) -> ai.ImageUrl | ai.BinaryContent:
    url = image_url.get("url", "") if isinstance(image_url, dict) else str(image_url)
    if url.startswith("data:"):
        header, _, data = url.partition(",")
        media_type = header.removeprefix("data:").split(";")[0] or "image/png"
        try:
            return ai.BinaryContent(data=base64.b64decode(data), media_type=media_type)
        except ValueError as e:
            raise GatewayError("Invalid image data URL") from e
    if not url:
        raise GatewayError("An image_url part needs a url")
    return ai.ImageUrl(url=url)


def _user_content(content: Any) -> str | list[ai.UserContent]:
    if isinstance(content, str) or content is None:
        return content or ""
    if not isinstance(content, list):
        raise GatewayError("A user message content must be a string or a list of parts")
    parts: list[ai.UserContent] = []
    for part in content:
        kind = part.get("type") if isinstance(part, dict) else None
        if kind == "text":
            parts.append(part.get("text", ""))
        elif kind == "image_url":
            parts.append(_image(part.get("image_url")))
        else:
            raise GatewayError(f"Unsupported user content part {kind!r}")
    return parts


def _tool_calls(message: dict) -> list[ai.ToolCallPart]:
    parts = []
    for call in message.get("tool_calls") or []:
        function = call.get("function") or {}
        name = function.get("name")
        if not name:
            raise GatewayError("A tool call needs a function name")
        parts.append(
            ai.ToolCallPart(
                tool_name=name,
                args=function.get("arguments") or "{}",
                tool_call_id=call.get("id") or f"call_{uuid.uuid4().hex[:24]}",
            )
        )
    return parts


def convert_messages(messages: list[dict]) -> list[ai.ModelMessage]:
    """Chat Completions messages as pydantic-ai's alternating requests and
    responses. Consecutive system/user/tool messages share one request.
    """
    if not isinstance(messages, list) or not messages:
        raise GatewayError("messages must be a non-empty list")
    converted: list[ai.ModelMessage] = []
    request_parts: list[ai.ModelRequestPart] = []
    tool_names: dict[str, str] = {}  # tool call id -> tool name

    def flush_request():
        if request_parts:
            converted.append(ai.ModelRequest(parts=list(request_parts)))
            request_parts.clear()

    for message in messages:
        if not isinstance(message, dict):
            raise GatewayError("Each message must be an object")
        role = message.get("role")
        content = message.get("content")
        if role in ("system", "developer"):
            request_parts.append(ai.SystemPromptPart(content=_text(content)))
        elif role == "user":
            request_parts.append(ai.UserPromptPart(content=_user_content(content)))
        elif role == "tool":
            call_id = message.get("tool_call_id")
            if not call_id:
                raise GatewayError("A tool message needs a tool_call_id")
            request_parts.append(
                ai.ToolReturnPart(
                    tool_name=tool_names.get(call_id, message.get("name") or "tool"),
                    content=_text(content),
                    tool_call_id=call_id,
                )
            )
        elif role == "assistant":
            flush_request()
            parts: list[ai.ModelResponsePart] = []
            text = _text(content)
            if text:
                parts.append(ai.TextPart(content=text))
            calls = _tool_calls(message)
            tool_names.update({call.tool_call_id: call.tool_name for call in calls})
            parts.extend(calls)
            converted.append(ai.ModelResponse(parts=parts))
        else:
            raise GatewayError(f"Unsupported message role {role!r}")
    flush_request()
    return converted


def convert_tools(tools: Any) -> list[ToolDefinition]:
    if not tools:
        return []
    if not isinstance(tools, list):
        raise GatewayError("tools must be a list")
    definitions = []
    for tool in tools:
        function = tool.get("function") if isinstance(tool, dict) else None
        if tool.get("type", "function") != "function" or not function:
            raise GatewayError("Only function tools are supported")
        if not function.get("name"):
            raise GatewayError("A tool needs a name")
        definitions.append(
            ToolDefinition(
                name=function["name"],
                description=function.get("description"),
                parameters_json_schema=function.get("parameters")
                or DEFAULT_TOOL_PARAMETERS,
            )
        )
    return definitions


def convert_settings(body: dict) -> dict[str, Any]:
    """The sampling parameters of the request, as pydantic-ai model settings."""
    settings: dict[str, Any] = {}
    for key in ("max_tokens", "temperature", "top_p", "seed", "parallel_tool_calls"):
        if body.get(key) is not None:
            settings[key] = body[key]
    if body.get("max_completion_tokens") is not None:
        settings["max_tokens"] = body["max_completion_tokens"]
    stop = body.get("stop")
    if stop:
        settings["stop_sequences"] = [stop] if isinstance(stop, str) else list(stop)
    tool_choice = body.get("tool_choice")
    if isinstance(tool_choice, str) and tool_choice in ("auto", "none", "required"):
        settings["tool_choice"] = tool_choice
    elif isinstance(tool_choice, dict):
        name = (tool_choice.get("function") or {}).get("name")
        if name:
            settings["tool_choice"] = [name]
    return settings


def parse_chat_request(body: Any) -> ChatRequest:
    if not isinstance(body, dict):
        raise GatewayError("The request body must be a JSON object")
    stream_options = body.get("stream_options") or {}
    return ChatRequest(
        messages=convert_messages(body.get("messages")),
        tools=convert_tools(body.get("tools")),
        settings=convert_settings(body),
        stream=bool(body.get("stream")),
        include_usage=bool(stream_options.get("include_usage")),
        requested_model=str(body.get("model") or ""),
    )


# ---------------------------------------------------------------------------
# Response: pydantic-ai -> Chat Completions
# ---------------------------------------------------------------------------


def _usage_json(usage: RequestUsage) -> dict:
    # Like Anthropic through litellm: prompt tokens include the cached ones.
    return {
        "prompt_tokens": usage.input_tokens,
        "completion_tokens": usage.output_tokens,
        "total_tokens": usage.input_tokens + usage.output_tokens,
        "prompt_tokens_details": {"cached_tokens": usage.cache_read_tokens},
    }


def _tool_call_json(index: int, part: ai.ToolCallPart) -> dict:
    return {
        "index": index,
        "id": part.tool_call_id,
        "type": "function",
        "function": {"name": part.tool_name, "arguments": part.args_as_json_str()},
    }


def _finish_reason(response: ai.ModelResponse) -> str:
    if response.finish_reason in FINISH_REASONS:
        return FINISH_REASONS[response.finish_reason]
    return "tool_calls" if response.tool_calls else "stop"


@dataclass
class Completion:
    """One run of the model, for the view to answer and account."""

    built_model: BuiltModel
    request: ChatRequest
    id: str = field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    created: int = field(default_factory=lambda: int(time.time()))
    response: ai.ModelResponse | None = None

    @property
    def model(self):
        # Spans like the agents' (gen_ai.* attributes), on the global tracer
        # provider Logfire configures; a no-op when it does not.
        return InstrumentedModel(self.built_model.model)

    @property
    def model_name(self) -> str:
        return self.built_model.api_name

    @property
    def usage(self) -> RequestUsage:
        return self.response.usage if self.response else RequestUsage()

    def _chunk(self, delta: dict, finish_reason: str | None = None, **extra) -> str:
        chunk = {
            "id": self.id,
            "object": "chat.completion.chunk",
            "created": self.created,
            "model": self.model_name,
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
            **extra,
        }
        return f"data: {json.dumps(chunk)}\n\n"

    async def complete(self) -> dict:
        """Run the model and answer the whole completion at once."""
        self.response = await self.model.request(
            self.request.messages,
            self.request.model_settings(),
            self.request.request_parameters,
        )
        text = "".join(
            p.content for p in self.response.parts if isinstance(p, ai.TextPart)
        )
        tool_calls = [
            _tool_call_json(i, part) for i, part in enumerate(self.response.tool_calls)
        ]
        message: dict[str, Any] = {"role": "assistant", "content": text or None}
        if tool_calls:
            message["tool_calls"] = tool_calls
        return {
            "id": self.id,
            "object": "chat.completion",
            "created": self.created,
            "model": self.model_name,
            "choices": [
                {
                    "index": 0,
                    "message": message,
                    "finish_reason": _finish_reason(self.response),
                }
            ],
            "usage": _usage_json(self.usage),
        }

    async def stream(self) -> AsyncIterator[str]:
        """Run the model and yield the completion as server-sent events.

        Text streams as it comes; tool calls are sent whole once the model is
        done, which the clients accept (they only act on complete calls).
        """
        yield self._chunk({"role": "assistant", "content": ""})
        async with self.model.request_stream(
            self.request.messages,
            self.request.model_settings(),
            self.request.request_parameters,
        ) as streamed:
            try:
                async for event in streamed:
                    if isinstance(event, ai.PartStartEvent) and isinstance(
                        event.part, ai.TextPart
                    ):
                        if event.part.content:
                            yield self._chunk({"content": event.part.content})
                    elif isinstance(event, ai.PartDeltaEvent) and isinstance(
                        event.delta, ai.TextPartDelta
                    ):
                        if event.delta.content_delta:
                            yield self._chunk({"content": event.delta.content_delta})
            finally:
                # Whatever the provider sent is billed, even when the client
                # left or the stream broke before the end.
                self.response = streamed.get()

        tool_calls = [
            _tool_call_json(i, part) for i, part in enumerate(self.response.tool_calls)
        ]
        if tool_calls:
            yield self._chunk({"tool_calls": tool_calls})
        yield self._chunk({}, finish_reason=_finish_reason(self.response))
        if self.request.include_usage:
            yield self._chunk({}, usage=_usage_json(self.usage))
        yield "data: [DONE]\n\n"


def error_event(message: str, error_type: str = "server_error") -> str:
    """An error in the middle of a stream, the way the OpenAI SDKs read it."""
    return (
        f"data: {json.dumps({'error': {'message': message, 'type': error_type}})}\n\n"
    )
