from django.test import SimpleTestCase

from hexa.assistant.ai_models.ids import ModelId


class ModelIdTest(SimpleTestCase):
    def test_parses_a_provider_prefixed_id(self):
        self.assertEqual(
            ModelId.parse("anthropic:claude-opus-4-6"),
            ModelId("anthropic", "claude-opus-4-6"),
        )

    def test_splits_on_the_first_separator_only(self):
        """Some providers put a colon in the model name itself."""
        self.assertEqual(
            ModelId.parse("bedrock:eu.anthropic.claude:0"),
            ModelId("bedrock", "eu.anthropic.claude:0"),
        )

    def test_a_bare_model_name_is_not_an_id(self):
        self.assertIsNone(ModelId.parse("opus"))

    def test_a_missing_half_is_not_an_id(self):
        self.assertIsNone(ModelId.parse("anthropic:"))
        self.assertIsNone(ModelId.parse(":claude-opus-4-6"))

    def test_a_value_that_is_not_a_string_is_not_an_id(self):
        """Ids come out of operator-written JSON, so anything can turn up."""
        self.assertIsNone(ModelId.parse(["haiku"]))
        self.assertIsNone(ModelId.parse(None))

    def test_the_region_is_not_part_of_the_id(self):
        """pydantic-ai reads the id as is, and knows nothing about regions."""
        self.assertEqual(
            str(ModelId("google-cloud", "gemini-3-pro-preview", region="eu")),
            "google-cloud:gemini-3-pro-preview",
        )

    def test_str_gives_back_the_id_it_was_parsed_from(self):
        self.assertEqual(
            str(ModelId.parse("google-cloud:gemini-3-pro-preview")),
            "google-cloud:gemini-3-pro-preview",
        )
