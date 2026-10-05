from decimal import Decimal

from anthropic import AsyncAnthropic
from anthropic.lib.vertex import AsyncAnthropicVertex
from anthropic.types.beta import BetaMessage, BetaTextBlock, BetaUsage
from asgiref.sync import async_to_sync
from django.test import SimpleTestCase
from google.genai.types import Candidate, Content, GenerateContentResponse, Part
from pydantic_ai import RunUsage
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google import GoogleProvider

from hexa.assistant.ai_models import BuiltModel
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation

from ._helpers import FakeModelBuilder, _AgentWithFakeTool
from ._testcase import AgentTestCase

_MODEL = "claude-opus-4-6"
_EPHEMERAL = {"type": "ephemeral", "ttl": "5m"}

_UNCACHED_TOKENS = 200
_CACHE_WRITE_TOKENS = 26_300
_CACHE_READ_TOKENS = 26_120


def _count_cache_points(request: dict) -> int:
    blocks = [*request["system"], *request["tools"]]
    for message in request["messages"]:
        blocks.extend(message["content"])
    explicit = sum(1 for block in blocks if "cache_control" in block)
    return explicit + (1 if isinstance(request.get("cache_control"), dict) else 0)


class PromptCachingRequestTest(AgentTestCase):
    """What actually goes over the wire, with the Anthropic client faked."""

    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def _run(self, client) -> tuple[dict, RunUsage]:
        requests = []

        async def create(**kwargs):
            requests.append(kwargs)
            return BetaMessage(
                id="msg-test",
                content=[BetaTextBlock(type="text", text="Done.")],
                model=_MODEL,
                role="assistant",
                stop_reason="end_turn",
                type="message",
                usage=BetaUsage(
                    input_tokens=_UNCACHED_TOKENS,
                    output_tokens=70,
                    cache_creation_input_tokens=_CACHE_WRITE_TOKENS,
                    cache_read_input_tokens=_CACHE_READ_TOKENS,
                ),
            )

        client.beta.messages.create = create
        model = AnthropicModel(
            _MODEL, provider=AnthropicProvider(anthropic_client=client)
        )
        agent = _AgentWithFakeTool(self.conversation, FakeModelBuilder(model))
        result = async_to_sync(agent.agent.run)("Hello")
        return requests[0], result.usage

    def _assert_prefix_is_cached(self, request: dict) -> None:
        self.assertEqual(
            [block.get("cache_control") for block in request["system"]], [_EPHEMERAL]
        )
        self.assertEqual(request["tools"][-1].get("cache_control"), _EPHEMERAL)
        self.assertLessEqual(_count_cache_points(request), 4)

    def test_vertex_caches_prefix_and_last_message(self):
        """Vertex has no top-level automatic caching, so pydantic-ai marks the
        last message itself.
        """
        request, _ = self._run(
            AsyncAnthropicVertex(
                project_id="project", region="us-east5", access_token="token"
            )
        )
        self._assert_prefix_is_cached(request)
        self.assertNotIsInstance(request.get("cache_control"), dict)
        self.assertEqual(
            request["messages"][-1]["content"][-1].get("cache_control"), _EPHEMERAL
        )

    def test_direct_anthropic_caches_prefix_and_conversation(self):
        request, _ = self._run(AsyncAnthropic(api_key="test-key"))
        self._assert_prefix_is_cached(request)
        self.assertEqual(request["cache_control"], _EPHEMERAL)

    def test_input_tokens_include_cached_tokens(self):
        """Message.input_tokens and Conversation.total_input_tokens store this
        number, so it must keep counting every prompt token, cached or not.
        """
        _, usage = self._run(AsyncAnthropic(api_key="test-key"))
        self.assertEqual(usage.cache_write_tokens, _CACHE_WRITE_TOKENS)
        self.assertEqual(usage.cache_read_tokens, _CACHE_READ_TOKENS)
        self.assertEqual(
            usage.input_tokens,
            _UNCACHED_TOKENS + _CACHE_WRITE_TOKENS + _CACHE_READ_TOKENS,
        )


class PromptCachingOtherProvidersTest(AgentTestCase):
    """The cache settings are Anthropic's; other providers must ignore them."""

    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def test_gemini_request_is_unaffected_by_anthropic_cache_settings(self):
        provider = GoogleProvider(api_key="test-key")
        requests = []

        async def generate_content(**kwargs):
            requests.append(kwargs)
            return GenerateContentResponse(
                candidates=[
                    Candidate(
                        content=Content(role="model", parts=[Part(text="Done.")]),
                        finish_reason="STOP",
                    )
                ],
            )

        provider.client.aio.models.generate_content = generate_content
        model = GoogleModel("gemini-2.5-pro", provider=provider)
        agent = _AgentWithFakeTool(self.conversation, FakeModelBuilder(model))
        async_to_sync(agent.agent.run)("Hello")

        config = requests[0]["config"]
        self.assertIsNone(config.get("cached_content"))
        self.assertIsNotNone(config.get("system_instruction"))
        self.assertTrue(config.get("tools"))
        self.assertNotIn("cache_control", str(requests[0]))


class PromptCachingCostTest(SimpleTestCase):
    def _cost(self, provider_id: str, usage: RunUsage) -> Decimal | None:
        return BuiltModel(
            model=TestModel(), api_name=_MODEL, provider_id=provider_id
        ).calculate_cost(usage)

    def test_cache_reads_and_writes_are_priced_at_their_own_rates(self):
        usage = RunUsage(
            input_tokens=_UNCACHED_TOKENS + _CACHE_WRITE_TOKENS + _CACHE_READ_TOKENS,
            cache_write_tokens=_CACHE_WRITE_TOKENS,
            cache_read_tokens=_CACHE_READ_TOKENS,
            output_tokens=70,
        )
        # USD per million tokens: 5 input, 6.25 cache write, 0.50 cache read, 25 output.
        expected = (
            _UNCACHED_TOKENS * Decimal("5")
            + _CACHE_WRITE_TOKENS * Decimal("6.25")
            + _CACHE_READ_TOKENS * Decimal("0.5")
            + 70 * Decimal("25")
        ) / 1_000_000
        for provider_id in ("google-vertex", "anthropic"):
            with self.subTest(provider_id=provider_id):
                self.assertEqual(self._cost(provider_id, usage), expected)

    def test_cached_run_costs_less_than_the_same_tokens_uncached(self):
        total = _UNCACHED_TOKENS + _CACHE_WRITE_TOKENS + _CACHE_READ_TOKENS
        cached = RunUsage(
            input_tokens=total,
            cache_write_tokens=_CACHE_WRITE_TOKENS,
            cache_read_tokens=_CACHE_READ_TOKENS,
        )
        self.assertLess(
            self._cost("google-vertex", cached),
            self._cost("google-vertex", RunUsage(input_tokens=total)),
        )
