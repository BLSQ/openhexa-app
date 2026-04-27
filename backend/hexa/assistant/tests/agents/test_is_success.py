from hexa.assistant.agents.base import _is_success
from hexa.core.test import TestCase


class IsSuccessTest(TestCase):
    def test_plain_dict_without_errors_is_success(self):
        self.assertTrue(_is_success({"data": {"pipeline": {"id": "1"}}}))

    def test_dict_with_errors_key_is_failure(self):
        self.assertFalse(_is_success({"errors": ["Something failed"]}))

    def test_dict_with_nested_errors_is_failure(self):
        self.assertFalse(_is_success({"createPipeline": {"errors": ["Invalid name"]}}))

    def test_non_json_string_is_failure(self):
        self.assertFalse(_is_success("this is not json"))

    def test_json_encoded_dict_without_errors_is_success(self):
        self.assertTrue(_is_success('{"pipeline": {"id": "abc"}}'))

    def test_json_encoded_dict_with_errors_is_failure(self):
        self.assertFalse(_is_success('{"errors": ["oops"]}'))

    def test_non_dict_content_is_success(self):
        self.assertTrue(_is_success(["a", "b"]))
        self.assertTrue(_is_success(42))
