from django.test import SimpleTestCase, override_settings

from hexa.assistant.agents import pinnable_agent_keys
from hexa.assistant.agents.naming_agent import NamingAgent
from hexa.assistant.model_builder import _MODEL_IDS_BY_PROVIDER, supports
from hexa.assistant.model_selection import resolve_model, warn_on_unknown_overrides
from hexa.user_management.models import AiSettings

_LOGGER = "hexa.assistant.model_selection"


def _ai_settings(model=AiSettings.Model.OPUS, provider=AiSettings.Provider.ANTHROPIC):
    return AiSettings(provider=provider, model=model, api_key="test-key", enabled=True)


class ResolveModelTest(SimpleTestCase):
    def test_agent_without_a_key_runs_on_the_organization_model(self):
        self.assertEqual(
            resolve_model(_ai_settings(), None, None), AiSettings.Model.OPUS
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"general": "haiku"}')
    def test_agent_without_a_key_ignores_the_environment(self):
        """Only agents that opt in can be pinned, so no entry can downgrade the
        organization's main assistant.
        """
        self.assertEqual(
            resolve_model(_ai_settings(), None, None), AiSettings.Model.OPUS
        )

    def test_agent_default_wins_over_the_organization_model(self):
        self.assertEqual(
            resolve_model(_ai_settings(), "naming", AiSettings.Model.HAIKU),
            AiSettings.Model.HAIKU,
        )

    def test_agent_without_a_default_runs_on_the_organization_model(self):
        self.assertEqual(
            resolve_model(_ai_settings(), "generate_sql", None), AiSettings.Model.OPUS
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "sonnet"}')
    def test_environment_wins_over_the_agent_default(self):
        self.assertEqual(
            resolve_model(_ai_settings(), "naming", AiSettings.Model.HAIKU),
            AiSettings.Model.SONNET,
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"generate_sql": "haiku"}')
    def test_environment_pins_an_agent_that_has_no_default(self):
        self.assertEqual(
            resolve_model(_ai_settings(), "generate_sql", None), AiSettings.Model.HAIKU
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"generate_sql": "sonnet"}')
    def test_falls_back_when_the_provider_does_not_expose_the_model(self):
        ai_settings = _ai_settings(provider=AiSettings.Provider.MANAGED)
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = resolve_model(ai_settings, "generate_sql", None)
        self.assertEqual(resolved, AiSettings.MANAGED_MODEL)


class OverridesParsingTest(SimpleTestCase):
    @override_settings(ASSISTANT_AGENT_MODELS="not json")
    def test_invalid_json_is_ignored(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = resolve_model(_ai_settings(), "naming", AiSettings.Model.HAIKU)
        self.assertEqual(resolved, AiSettings.Model.HAIKU)

    @override_settings(ASSISTANT_AGENT_MODELS='["naming"]')
    def test_json_that_is_not_an_object_is_ignored(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = resolve_model(_ai_settings(), "naming", AiSettings.Model.HAIKU)
        self.assertEqual(resolved, AiSettings.Model.HAIKU)

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "gpt-9"}')
    def test_unknown_model_falls_back_to_the_agent_default(self):
        with self.assertLogs(_LOGGER, level="ERROR"):
            resolved = resolve_model(_ai_settings(), "naming", AiSettings.Model.HAIKU)
        self.assertEqual(resolved, AiSettings.Model.HAIKU)

    @override_settings(ASSISTANT_AGENT_MODELS='{"nmaing": "haiku"}')
    def test_entry_for_an_agent_that_cannot_be_pinned_is_reported(self):
        with self.assertLogs(_LOGGER, level="ERROR") as logs:
            warn_on_unknown_overrides(pinnable_agent_keys())
        self.assertIn("nmaing", logs.output[0])

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "haiku"}')
    def test_entry_for_a_pinnable_agent_is_not_reported(self):
        with self.assertNoLogs(_LOGGER, level="ERROR"):
            warn_on_unknown_overrides(pinnable_agent_keys())


class PinnableAgentsTest(SimpleTestCase):
    def test_only_the_documented_agents_can_be_pinned(self):
        """Widening this set lets an operator change the model of a user-facing
        agent from the environment, so it should be a deliberate change.
        """
        self.assertEqual(pinnable_agent_keys(), {"naming", "generate_sql"})

    def test_every_provider_exposes_the_naming_default(self):
        """A provider whose map lacks it silently loses the cost saving, so catch
        it here rather than in production logs.
        """
        for provider in _MODEL_IDS_BY_PROVIDER:
            with self.subTest(provider=provider):
                self.assertTrue(supports(provider, NamingAgent.default_model))
