from django.test import SimpleTestCase, override_settings

from hexa.assistant.agents.keys import AgentKey
from hexa.assistant.agents.naming_agent import NamingAgent
from hexa.assistant.model_builder import _MODEL_IDS_BY_PROVIDER, supports
from hexa.assistant.model_selection import resolve_model
from hexa.user_management.models import AiSettings

_LOGGER = "hexa.assistant.model_selection"


def _ai_settings(model=AiSettings.Model.OPUS, provider=AiSettings.Provider.ANTHROPIC):
    return AiSettings(provider=provider, model=model, api_key="test-key", enabled=True)


class ResolveModelTest(SimpleTestCase):
    def test_agent_without_a_default_runs_on_the_organization_model(self):
        self.assertEqual(
            resolve_model(_ai_settings(), AgentKey.GENERAL, None),
            AiSettings.Model.OPUS,
        )

    def test_agent_default_wins_over_the_organization_model(self):
        self.assertEqual(
            resolve_model(_ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU),
            AiSettings.Model.HAIKU,
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "sonnet"}')
    def test_environment_wins_over_the_agent_default(self):
        self.assertEqual(
            resolve_model(_ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU),
            AiSettings.Model.SONNET,
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"general": "haiku"}')
    def test_every_agent_can_be_pinned(self):
        self.assertEqual(
            resolve_model(_ai_settings(), AgentKey.GENERAL, None),
            AiSettings.Model.HAIKU,
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "haiku"}')
    def test_an_entry_leaves_the_other_agents_alone(self):
        self.assertEqual(
            resolve_model(_ai_settings(), AgentKey.GENERATE_SQL, None),
            AiSettings.Model.OPUS,
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"generate_sql": "sonnet"}')
    def test_falls_back_when_the_provider_does_not_expose_the_model(self):
        ai_settings = _ai_settings(provider=AiSettings.Provider.MANAGED)
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = resolve_model(ai_settings, AgentKey.GENERATE_SQL, None)
        self.assertEqual(resolved, AiSettings.MANAGED_MODEL)


class OverridesParsingTest(SimpleTestCase):
    """A bad entry is dropped on its own, so the pins set alongside it — which
    may be the deliberate ones — still apply.
    """

    def _assert_entry_ignored(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = resolve_model(
                _ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU
            )
        self.assertEqual(resolved, AiSettings.Model.HAIKU)

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
            resolved = resolve_model(_ai_settings(), AgentKey.GENERATE_SQL, None)
        self.assertEqual(resolved, AiSettings.Model.HAIKU)

    @override_settings(ASSISTANT_AGENT_MODELS="not json")
    def test_invalid_json_is_ignored(self):
        self._assert_entry_ignored()

    @override_settings(ASSISTANT_AGENT_MODELS='["naming"]')
    def test_json_that_is_not_an_object_is_ignored(self):
        self._assert_entry_ignored()

    @override_settings(ASSISTANT_AGENT_MODELS="")
    def test_an_empty_setting_leaves_the_defaults_alone(self):
        with self.assertNoLogs(_LOGGER, level="ERROR"):
            resolved = resolve_model(
                _ai_settings(), AgentKey.NAMING, AiSettings.Model.HAIKU
            )
        self.assertEqual(resolved, AiSettings.Model.HAIKU)


class AgentKeysTest(SimpleTestCase):
    def test_every_provider_exposes_the_naming_default(self):
        """A provider whose map lacks it silently loses the cost saving, so catch
        it here rather than in production logs.
        """
        for provider in _MODEL_IDS_BY_PROVIDER:
            with self.subTest(provider=provider):
                self.assertTrue(supports(provider, NamingAgent.default_model))
