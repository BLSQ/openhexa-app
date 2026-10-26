"""The OpenAI-compatible gateway the notebook servers' AI tooling calls."""

import base64
import json
from decimal import Decimal
from unittest.mock import patch

import genai_prices
from asgiref.sync import async_to_sync
from genai_prices.types import Usage
from pydantic_ai import messages as ai
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel

from hexa.assistant.ai_models import BuiltModel
from hexa.assistant.exceptions import AssistantException
from hexa.assistant.models import AiUsage
from hexa.assistant.notebooks import gateway, views
from hexa.core.test import TestCase
from hexa.core.test.utils import collect_async_stream
from hexa.user_management.models import AiSettings, User
from hexa.workspaces.authentication import WorkspaceToken
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

URL = "/assistant/gateway/v1/chat/completions"
BUILD = "hexa.assistant.notebooks.views.AiModelBuilder.build_for_agent"
PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n").decode()


def _events(content: bytes) -> list:
    """The data of each server-sent event; "[DONE]" as is."""
    events = []
    for block in content.decode().split("\n\n"):
        for line in block.splitlines():
            if line.startswith("data: "):
                data = line[len("data: ") :]
                events.append(data if data == "[DONE]" else json.loads(data))
    return events


def _text_model(text="Hello world", model_name="claude-opus-4-6") -> FunctionModel:
    def function(messages, info: AgentInfo) -> ai.ModelResponse:
        return ai.ModelResponse(parts=[ai.TextPart(content=text)])

    async def stream(messages, info: AgentInfo):
        for word in text.split(" "):
            yield word + " "

    return FunctionModel(function, stream_function=stream, model_name=model_name)


def _tool_model() -> FunctionModel:
    def function(messages, info: AgentInfo) -> ai.ModelResponse:
        return ai.ModelResponse(
            parts=[
                ai.TextPart(content="Running it."),
                ai.ToolCallPart(
                    tool_name="run_cell", args={"cell": 1}, tool_call_id="call_1"
                ),
            ]
        )

    async def stream(messages, info: AgentInfo):
        yield "Running it."
        yield {
            0: DeltaToolCall(
                name="run_cell", json_args='{"cell": 1}', tool_call_id="call_1"
            )
        }

    return FunctionModel(function, stream_function=stream, model_name="claude-opus-4-6")


def _failing_model() -> FunctionModel:
    def function(messages, info: AgentInfo):
        raise RuntimeError("provider down")

    async def stream(messages, info: AgentInfo):
        yield "partial "
        raise RuntimeError("provider down")

    return FunctionModel(function, stream_function=stream, model_name="claude-opus-4-6")


def _built(model, provider_id="google-vertex") -> BuiltModel:
    return BuiltModel(model=model, api_name=model.model_name, provider_id=provider_id)


class ConvertMessagesTest(TestCase):
    def test_system_and_user_share_a_request(self):
        (request,) = gateway.convert_messages(
            [
                {"role": "system", "content": "Be brief."},
                {"role": "user", "content": [{"type": "text", "text": "Hi"}]},
            ]
        )
        self.assertIsInstance(request, ai.ModelRequest)
        system, user = request.parts
        self.assertEqual(system.content, "Be brief.")
        self.assertEqual(user.content, ["Hi"])

    def test_tool_round_trip(self):
        messages = gateway.convert_messages(
            [
                {"role": "user", "content": "Run cell 1"},
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "run_cell",
                                "arguments": '{"cell": 1}',
                            },
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "call_1", "content": "ok"},
                {"role": "user", "content": "Thanks"},
            ]
        )
        self.assertEqual(
            [type(m) for m in messages],
            [ai.ModelRequest, ai.ModelResponse, ai.ModelRequest],
        )
        (call,) = messages[1].parts
        self.assertEqual(
            (call.tool_name, call.args_as_dict(), call.tool_call_id),
            ("run_cell", {"cell": 1}, "call_1"),
        )
        tool_return, user = messages[2].parts
        self.assertEqual(
            (tool_return.tool_name, tool_return.content, tool_return.tool_call_id),
            ("run_cell", "ok", "call_1"),
        )
        self.assertEqual(user.content, "Thanks")

    def test_images(self):
        (request,) = gateway.convert_messages(
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is this?"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{PNG}"},
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": "https://example.org/a.png"},
                        },
                    ],
                }
            ]
        )
        text, binary, url = request.parts[0].content
        self.assertEqual(text, "What is this?")
        self.assertEqual(
            (binary.media_type, binary.data[:4]), ("image/png", b"\x89PNG")
        )
        self.assertEqual(url.url, "https://example.org/a.png")

    def test_extra_keys_such_as_cache_control_are_ignored(self):
        (request,) = gateway.convert_messages(
            [{"role": "system", "content": "x", "cache_control": {"type": "ephemeral"}}]
        )
        self.assertEqual(request.parts[0].content, "x")

    def test_rejects_what_it_cannot_run(self):
        for messages in (
            [],
            [{"role": "function", "content": "x"}],
            [{"role": "tool", "content": "x"}],
        ):
            with self.assertRaises(gateway.GatewayError):
                gateway.convert_messages(messages)

    def test_tools_and_settings(self):
        request = gateway.parse_chat_request(
            {
                "model": "whatever",
                "messages": [{"role": "user", "content": "x"}],
                "tools": [
                    {"type": "function", "function": {"name": "f", "description": "d"}}
                ],
                "stream": True,
                "stream_options": {"include_usage": True},
                "temperature": 0.2,
                "max_tokens": 50,
                "stop": "END",
                "tool_choice": {"type": "function", "function": {"name": "f"}},
            }
        )
        (tool,) = request.tools
        self.assertEqual(
            (tool.name, tool.description, tool.parameters_json_schema),
            ("f", "d", gateway.DEFAULT_TOOL_PARAMETERS),
        )
        self.assertTrue(request.stream and request.include_usage)
        self.assertEqual(
            request.settings,
            {
                "temperature": 0.2,
                "max_tokens": 50,
                "stop_sequences": ["END"],
                "tool_choice": ["f"],
            },
        )
        self.assertEqual(request.model_settings()["max_tokens"], 50)
        self.assertEqual(request.requested_model, "whatever")


class GatewayViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("jane@bluesquarehub.com", "janerocks2")
        cls.WORKSPACE = create_workspace(name="Gateway Workspace")
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

    def post(self, body: dict, token=None):
        return self.client.post(
            URL,
            data=json.dumps(body),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token or self.TOKEN}",
        )

    def stream(self, body: dict, model):
        with patch(BUILD, return_value=_built(model)):
            response = self.post({**body, "stream": True})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "text/event-stream")
            # async_to_sync keeps the ORM on this thread, inside the test transaction.
            content = async_to_sync(collect_async_stream)(response.streaming_content)
        return _events(content)

    MESSAGES = [{"role": "user", "content": "Say hello"}]

    def test_streams_text_then_finish_usage_and_done(self):
        events = self.stream(
            {"messages": self.MESSAGES, "stream_options": {"include_usage": True}},
            _text_model("Hello world"),
        )
        self.assertEqual(events[-1], "[DONE]")
        chunks = events[:-1]
        self.assertTrue(
            all(
                c["object"] == "chat.completion.chunk"
                and c["model"] == "claude-opus-4-6"
                for c in chunks
            )
        )
        self.assertEqual(chunks[0]["choices"][0]["delta"]["role"], "assistant")
        text = "".join(c["choices"][0]["delta"].get("content") or "" for c in chunks)
        self.assertEqual(text, "Hello world ")
        finish = [
            c["choices"][0]["finish_reason"]
            for c in chunks
            if c["choices"][0]["finish_reason"]
        ]
        self.assertEqual(finish, ["stop"])
        usage = chunks[-1]["usage"]
        self.assertGreater(usage["prompt_tokens"], 0)
        self.assertGreater(usage["completion_tokens"], 0)
        self.assertEqual(
            usage["total_tokens"], usage["prompt_tokens"] + usage["completion_tokens"]
        )

    def test_streams_tool_calls_whole(self):
        events = self.stream(
            {
                "messages": self.MESSAGES,
                "tools": [{"type": "function", "function": {"name": "run_cell"}}],
            },
            _tool_model(),
        )
        chunks = events[:-1]
        tool_chunks = [c for c in chunks if "tool_calls" in c["choices"][0]["delta"]]
        self.assertEqual(len(tool_chunks), 1)
        (call,) = tool_chunks[0]["choices"][0]["delta"]["tool_calls"]
        self.assertEqual(call["index"], 0)
        self.assertEqual(call["id"], "call_1")
        self.assertEqual(call["function"]["name"], "run_cell")
        self.assertEqual(json.loads(call["function"]["arguments"]), {"cell": 1})
        self.assertEqual(chunks[-1]["choices"][0]["finish_reason"], "tool_calls")
        self.assertIn(
            "Running it.",
            "".join(c["choices"][0]["delta"].get("content") or "" for c in chunks),
        )

    def test_charges_the_organization(self):
        self.stream({"messages": self.MESSAGES}, _text_model())
        usage = AiUsage.objects.get()
        self.assertEqual(
            (usage.organization, usage.workspace, usage.user),
            (self.ORGANIZATION, self.WORKSPACE, self.USER),
        )
        self.assertEqual(
            (usage.source, usage.provider, usage.model_name),
            (AiUsage.Source.NOTEBOOK, "google-vertex", "claude-opus-4-6"),
        )
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)
        expected = genai_prices.calc_price(
            Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
            "claude-opus-4-6",
            provider_id="google-vertex",
        ).total_price
        self.assertEqual(usage.cost, Decimal(expected).quantize(Decimal("0.000001")))
        self.assertEqual(
            self.ORGANIZATION.get_monthly_ai_cost(), float(round(usage.cost, 2))
        )

    def test_non_streaming_completion(self):
        with patch(BUILD, return_value=_built(_tool_model())):
            response = self.post({"messages": self.MESSAGES})
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(payload["object"], "chat.completion")
        self.assertEqual(payload["model"], "claude-opus-4-6")
        (choice,) = payload["choices"]
        self.assertEqual(choice["finish_reason"], "tool_calls")
        self.assertEqual(choice["message"]["content"], "Running it.")
        self.assertEqual(
            choice["message"]["tool_calls"][0]["function"]["name"], "run_cell"
        )
        self.assertGreater(payload["usage"]["total_tokens"], 0)
        self.assertEqual(AiUsage.objects.count(), 1)

    def test_the_request_runs_on_the_organization_model(self):
        """Whatever model the client names, the organization's runs."""
        with patch(BUILD, return_value=_built(_text_model())) as build:
            response = self.post({"model": "gpt-5", "messages": self.MESSAGES})
        self.assertEqual(response.status_code, 200)
        build.assert_called_once_with("notebooks", None)
        self.assertEqual(response.json()["model"], "claude-opus-4-6")

    def test_requires_a_workspace_token(self):
        response = self.client.post(
            URL,
            data=json.dumps({"messages": self.MESSAGES}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["type"], "invalid_request_error")
        response = self.post({"messages": self.MESSAGES}, token="nope")
        self.assertEqual(response.status_code, 401)
        self.client.force_login(self.USER)
        response = self.client.post(
            URL,
            data=json.dumps({"messages": self.MESSAGES}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_refuses_when_the_assistant_is_off(self):
        AiSettings.objects.filter(organization=self.ORGANIZATION).update(enabled=False)
        response = self.post({"messages": self.MESSAGES})
        self.assertEqual(response.status_code, 403)
        self.assertIn("not enabled", response.json()["error"]["message"])

    def test_refuses_when_the_budget_is_spent(self):
        with patch(
            "hexa.user_management.models.Organization.is_ai_budget_limit_reached",
            return_value=True,
        ):
            response = self.post({"messages": self.MESSAGES})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["error"]["message"], "Organization AI budget exceeded"
        )

    def test_bad_requests(self):
        response = self.client.post(
            URL,
            data=b"{",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.TOKEN}",
        )
        self.assertEqual(response.status_code, 400)
        response = self.post({"messages": []})
        self.assertEqual(response.status_code, 400)
        response = self.post({"messages": [{"role": "robot", "content": "x"}]})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            self.client.get(URL, HTTP_AUTHORIZATION=f"Bearer {self.TOKEN}").status_code,
            405,
        )

    def test_no_model_available(self):
        with patch(BUILD, side_effect=AssistantException("nothing configured")):
            response = self.post({"messages": self.MESSAGES})
        self.assertEqual(response.status_code, 503)

    def test_model_failure(self):
        with patch(BUILD, return_value=_built(_failing_model())):
            response = self.post({"messages": self.MESSAGES})
        self.assertEqual(response.status_code, 502)
        self.assertEqual(AiUsage.objects.count(), 0)

        # Mid-stream, the provider billed us for what it sent before failing.
        events = self.stream({"messages": self.MESSAGES}, _failing_model())
        self.assertEqual(events[-1]["error"]["type"], "server_error")
        self.assertNotIn("[DONE]", events)
        self.assertEqual(
            "".join(c["choices"][0]["delta"].get("content") or "" for c in events[:-1]),
            "partial ",
        )
        self.assertGreater(AiUsage.objects.get().output_tokens, 0)

    def test_charges_what_a_disconnected_client_consumed(self):
        """Jupyternaut's Stop button closes the response mid-stream; the
        tokens the model produced until then are charged all the same.
        """
        completion = gateway.Completion(
            _built(_text_model("one two three four five")),
            gateway.parse_chat_request({"messages": self.MESSAGES, "stream": True}),
        )

        async def record():
            await views._record_gateway_usage(
                completion,
                organization=self.ORGANIZATION,
                workspace=self.WORKSPACE,
                user=self.USER,
            )

        async def read_two_chunks_then_leave():
            stream = views._stream_completion(completion, {}, record)
            await anext(stream)
            await anext(stream)
            await stream.aclose()

        async_to_sync(read_two_chunks_then_leave)()
        usage = AiUsage.objects.get()
        self.assertEqual(usage.source, AiUsage.Source.NOTEBOOK)
        self.assertGreater(usage.output_tokens, 0)
