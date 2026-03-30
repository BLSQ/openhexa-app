from unittest.mock import MagicMock

from django.test import SimpleTestCase, TestCase

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.model_builder import AiModelBuilder, get_api_name
from hexa.user_management.models import AiSettings


class GetApiNameTest(SimpleTestCase):
    def test_haiku_maps_to_correct_api_name(self):
        self.assertEqual(get_api_name(AiSettings.Model.HAIKU), "claude-haiku-4-5-20251001")

    def test_sonnet_maps_to_correct_api_name(self):
        self.assertEqual(get_api_name(AiSettings.Model.SONNET), "claude-sonnet-4-6")

    def test_opus_maps_to_correct_api_name(self):
        self.assertEqual(get_api_name(AiSettings.Model.OPUS), "claude-opus-4-6")

    def test_unknown_model_raises_assistant_exception(self):
        with self.assertRaises(AssistantException):
            get_api_name("no-such-model")


class AiModelBuilderTest(TestCase):
    def test_properties_reflect_constructor_args(self):
        builder = AiModelBuilder(
            provider=AiSettings.Provider.ANTHROPIC,
            model=AiSettings.Model.HAIKU,
            api_key="test-key",
        )
        self.assertEqual(builder.model_api_name, "claude-haiku-4-5-20251001")
        self.assertEqual(builder.provider_id, AiSettings.Provider.ANTHROPIC)

    def test_build_unsupported_provider_raises_value_error(self):
        builder = AiModelBuilder(
            provider="unsupported",
            model=AiSettings.Model.HAIKU,
            api_key="test-key",
        )
        with self.assertRaises(ValueError):
            builder.build()

    def test_from_conversation_raises_when_ai_settings_disabled(self):
        mock_conversation = MagicMock()
        mock_conversation.user.ai_settings_safe.enabled = False
        with self.assertRaises(AssistantException):
            AiModelBuilder.from_conversation(mock_conversation)
