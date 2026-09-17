from django.test import SimpleTestCase, override_settings
from pydantic_ai import RunUsage

from hexa.assistant.agents.keys import AgentKey
from hexa.assistant.agents.naming_agent import NamingAgent
from hexa.assistant.exceptions import AssistantException
from hexa.assistant.model_backend import (
    BringYourOwnKeyBackend,
    ManagedBackend,
    backend_for,
)
from hexa.assistant.model_builder import BuiltModel
from hexa.assistant.model_selection import ModelSelector
from hexa.user_management.models import AiSettings

# Parsing errors are reported by model_config and selection ones by
# model_selection; tests care that the entry was rejected, not by which module.
_LOGGER = "hexa.assistant"

_HAIKU_ID = "anthropic:claude-haiku-4-5"
_OPUS_ID = "anthropic:claude-opus-4-6"
_SONNET_ID = "anthropic:claude-sonnet-4-6"
_GEMINI_ID = "google-cloud:gemini-3-pro-preview"

# Every logical model we ship, as (provider, logical model, model id).
_SHIPPED_MODELS = [
    (AiSettings.Provider.MANAGED, model, model_id)
    for model, model_id in ManagedBackend.DEFAULT_MODEL_IDS.items()
] + [
    (provider, model, model_id)
    for provider, ids in BringYourOwnKeyBackend.MODEL_IDS.items()
    for model, model_id in ids.items()
]


def _ai_settings(model=AiSettings.Model.OPUS, provider=AiSettings.Provider.ANTHROPIC):
    return AiSettings(provider=provider, model=model, api_key="test-key", enabled=True)


def _managed_settings():
    return _ai_settings(provider=AiSettings.Provider.MANAGED, model=None)


def _selector(ai_settings: AiSettings) -> ModelSelector:
    return ModelSelector(backend_for(ai_settings))


def _for_agent(ai_settings, agent_key, default_model=None) -> str:
    return str(_selector(ai_settings).for_agent(agent_key, default_model))


def _for_organization(ai_settings) -> str:
    return str(_selector(ai_settings).for_organization())


class ForAgentTest(SimpleTestCase):
    def test_agent_without_a_default_runs_on_the_organization_model(self):
        self.assertEqual(_for_agent(_ai_settings(), AgentKey.GENERAL), _OPUS_ID)

    def test_agent_default_wins_over_the_organization_model(self):
        self.assertEqual(
            _for_agent(_ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU),
            _HAIKU_ID,
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "sonnet"}')
    def test_environment_wins_over_the_agent_default(self):
        self.assertEqual(
            _for_agent(_ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU),
            _SONNET_ID,
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"general": "haiku"}')
    def test_every_agent_can_be_pinned(self):
        self.assertEqual(_for_agent(_ai_settings(), AgentKey.GENERAL), _HAIKU_ID)

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "haiku"}')
    def test_an_entry_leaves_the_other_agents_alone(self):
        self.assertEqual(_for_agent(_ai_settings(), AgentKey.GENERATE_SQL), _OPUS_ID)

    @override_settings(ASSISTANT_AGENT_MODELS='{"generate_sql": "sonnet"}')
    def test_falls_back_when_the_provider_has_no_id_for_the_model(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = _for_agent(_managed_settings(), AgentKey.GENERATE_SQL)
        self.assertEqual(resolved, _OPUS_ID)


class LiteralPinTest(SimpleTestCase):
    """A pin may name a model id outright, which is the only way to put one agent
    on a different provider than the rest.
    """

    @override_settings(
        ASSISTANT_AGENT_MODELS='{"generate_sql": "google-cloud:gemini-3-pro-preview"}'
    )
    def test_a_model_id_pin_is_used_as_is(self):
        self.assertEqual(
            _for_agent(_managed_settings(), AgentKey.GENERATE_SQL), _GEMINI_ID
        )

    @override_settings(
        ASSISTANT_AGENT_MODELS='{"generate_sql": "google-cloud:gemini-3-pro-preview"}'
    )
    def test_falls_back_when_the_organization_holds_no_credentials_for_it(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = _for_agent(_ai_settings(), AgentKey.GENERATE_SQL)
        self.assertEqual(resolved, _OPUS_ID)

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "anthropic:some-new-model"}')
    def test_an_unreleased_model_needs_no_catalog_entry(self):
        self.assertEqual(
            _for_agent(_ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU),
            "anthropic:some-new-model",
        )


class ManagedModelsSettingTest(SimpleTestCase):
    """ASSISTANT_MANAGED_MODELS moves managed organizations onto another model.

    BYOK organizations pick their own model, so the setting must leave them alone.
    """

    @override_settings(ASSISTANT_MANAGED_MODELS='{"opus": "anthropic:claude-opus-5"}')
    def test_an_entry_overrides_the_default_id(self):
        self.assertEqual(
            _for_organization(_managed_settings()), "anthropic:claude-opus-5"
        )

    @override_settings(
        ASSISTANT_MANAGED_MODELS='{"opus": "google-cloud:gemini-3-pro-preview"}'
    )
    def test_managed_can_be_moved_to_another_provider_entirely(self):
        self.assertEqual(_for_organization(_managed_settings()), _GEMINI_ID)

    @override_settings(ASSISTANT_MANAGED_MODELS='{"opus": "anthropic:claude-opus-5"}')
    def test_models_left_out_keep_their_default(self):
        self.assertEqual(
            _for_agent(_managed_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU),
            _HAIKU_ID,
        )

    @override_settings(ASSISTANT_MANAGED_MODELS='{"opus": "anthropic:claude-opus-5"}')
    def test_bring_your_own_key_organizations_are_left_alone(self):
        self.assertEqual(_for_organization(_ai_settings()), _OPUS_ID)

    @override_settings(ASSISTANT_MANAGED_MODELS='{"opus": "claude-opus-5"}')
    def test_an_id_without_a_provider_prefix_is_ignored(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            self.assertEqual(_for_organization(_managed_settings()), _OPUS_ID)

    @override_settings(ASSISTANT_MANAGED_MODELS='{"gpt": "x:y"}')
    def test_an_unknown_model_is_ignored(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            self.assertEqual(_for_organization(_managed_settings()), _OPUS_ID)

    @override_settings(
        ASSISTANT_MANAGED_MODELS='{"gpt": "x:y", "opus": "anthropic:claude-opus-5"}'
    )
    def test_a_bad_entry_leaves_the_others_applied(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = _for_organization(_managed_settings())
        self.assertEqual(resolved, "anthropic:claude-opus-5")

    @override_settings(ASSISTANT_MANAGED_MODELS="not json")
    def test_invalid_json_leaves_the_defaults_alone(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            self.assertEqual(_for_organization(_managed_settings()), _OPUS_ID)

    @override_settings(ASSISTANT_MANAGED_MODELS="")
    def test_an_empty_setting_leaves_the_defaults_alone(self):
        with self.assertNoLogs(_LOGGER, level="ERROR"):
            self.assertEqual(_for_organization(_managed_settings()), _OPUS_ID)


class ForOrganizationTest(SimpleTestCase):
    def test_raises_when_no_id_is_configured_for_the_organization(self):
        """Every model in the enum maps to an id, so only a provider we know
        nothing about can leave an organization without one.
        """
        ai_settings = _ai_settings()
        ai_settings.provider = "no-such-provider"
        with self.assertRaises(AssistantException):
            _for_organization(ai_settings)


class PinsParsingTest(SimpleTestCase):
    """A bad entry is dropped on its own, so the pins set alongside it — which
    may be the deliberate ones — still apply.
    """

    def _assert_entry_ignored(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = _for_agent(
                _ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU
            )
        self.assertEqual(resolved, _HAIKU_ID)

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "gpt-9"}')
    def test_unknown_model_is_ignored(self):
        self._assert_entry_ignored()

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": ["haiku"]}')
    def test_a_model_that_is_not_a_string_is_ignored(self):
        self._assert_entry_ignored()

    @override_settings(ASSISTANT_AGENT_MODELS='{"nmaing": "sonnet"}')
    def test_unknown_agent_key_is_ignored(self):
        self._assert_entry_ignored()

    @override_settings(
        ASSISTANT_AGENT_MODELS='{"nmaing": "sonnet", "generate_sql": "haiku"}'
    )
    def test_a_bad_entry_leaves_the_others_applied(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = _for_agent(_ai_settings(), AgentKey.GENERATE_SQL)
        self.assertEqual(resolved, _HAIKU_ID)

    @override_settings(ASSISTANT_AGENT_MODELS="not json")
    def test_invalid_json_is_ignored(self):
        self._assert_entry_ignored()

    @override_settings(ASSISTANT_AGENT_MODELS='["naming"]')
    def test_json_that_is_not_an_object_is_ignored(self):
        self._assert_entry_ignored()

    @override_settings(ASSISTANT_AGENT_MODELS="")
    def test_an_empty_setting_leaves_the_defaults_alone(self):
        with self.assertNoLogs(_LOGGER, level="ERROR"):
            resolved = _for_agent(
                _ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU
            )
        self.assertEqual(resolved, _HAIKU_ID)


class CatalogPricingTest(SimpleTestCase):
    """Every model we ship has to be priceable.

    An unpriceable model costs nothing as far as we can tell, so its usage never
    counts towards ASSISTANT_MONTHLY_LIMIT and the cap silently stops applying.
    That is invisible in production, so catch a bad default here.
    """

    def test_every_default_model_can_be_priced(self):
        usage = RunUsage(input_tokens=1000, output_tokens=1000)
        for provider, model, model_id in _SHIPPED_MODELS:
            with self.subTest(provider=provider, model=model):
                backend = backend_for(_ai_settings(provider=provider))
                built = BuiltModel(
                    model=None,
                    api_name=model_id.name,
                    provider_id=backend.pricing_provider(model_id),
                )
                self.assertIsNotNone(
                    built.calculate_cost(usage),
                    f"genai_prices does not know {str(model_id)!r}",
                )


class AgentDefaultsTest(SimpleTestCase):
    def test_every_provider_maps_the_naming_default(self):
        """A provider whose map lacks it silently loses the cost saving, so catch
        it here rather than in production logs.
        """
        for provider, ids in [
            (AiSettings.Provider.MANAGED, ManagedBackend.DEFAULT_MODEL_IDS),
            *BringYourOwnKeyBackend.MODEL_IDS.items(),
        ]:
            with self.subTest(provider=provider):
                self.assertIn(NamingAgent.default_model, ids)
