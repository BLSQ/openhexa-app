from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolReturnPart,
    UserPromptPart,
)

from hexa.assistant.agents.base import (
    _strip_proposal_outputs,
    _summarize_proposal_output,
)
from hexa.core.test import TestCase

_FULL_OUTPUT = {
    "files": [
        {"path": "index.html", "content": "<h1>Hello</h1>"},
        {"path": "style.css", "content": "body { color: red; }"},
    ]
}


def _request_with_return(tool_name: str, content) -> ModelRequest:
    return ModelRequest(
        parts=[
            ToolReturnPart(tool_name=tool_name, content=content, tool_call_id="call-1")
        ]
    )


class SummarizeProposalOutputTest(TestCase):
    def test_success_output_is_summarized_to_paths(self):
        self.assertEqual(
            _summarize_proposal_output(_FULL_OUTPUT),
            {"status": "ok", "files": ["index.html", "style.css"]},
        )

    def test_error_output_is_kept(self):
        self.assertIsNone(_summarize_proposal_output({"error": "No changes provided"}))

    def test_json_string_output_is_summarized(self):
        self.assertEqual(
            _summarize_proposal_output('{"files": [{"path": "a.js", "content": "x"}]}'),
            {"status": "ok", "files": ["a.js"]},
        )

    def test_non_dict_output_is_kept(self):
        self.assertIsNone(_summarize_proposal_output("not json at all"))
        self.assertIsNone(_summarize_proposal_output(["a", "b"]))


class StripProposalOutputsTest(TestCase):
    def test_matching_tool_return_is_replaced(self):
        messages = [_request_with_return("propose_webapp_version", _FULL_OUTPUT)]
        stripped = _strip_proposal_outputs(messages, {"propose_webapp_version"})
        self.assertEqual(
            stripped[0].parts[0].content,
            {"status": "ok", "files": ["index.html", "style.css"]},
        )

    def test_other_tools_are_untouched(self):
        messages = [_request_with_return("read_file", _FULL_OUTPUT)]
        stripped = _strip_proposal_outputs(messages, {"propose_webapp_version"})
        self.assertEqual(stripped[0].parts[0].content, _FULL_OUTPUT)

    def test_error_return_is_untouched(self):
        error = {"error": "old_string not found"}
        messages = [_request_with_return("propose_webapp_version", error)]
        stripped = _strip_proposal_outputs(messages, {"propose_webapp_version"})
        self.assertEqual(stripped[0].parts[0].content, error)

    def test_non_request_messages_are_untouched(self):
        response = ModelResponse(parts=[TextPart(content="Done.")])
        stripped = _strip_proposal_outputs([response], {"propose_webapp_version"})
        self.assertEqual(stripped, [response])

    def test_original_messages_are_not_mutated(self):
        request = _request_with_return("propose_webapp_version", _FULL_OUTPUT)
        user_request = ModelRequest(parts=[UserPromptPart(content="hi")])
        _strip_proposal_outputs([request, user_request], {"propose_webapp_version"})
        self.assertEqual(request.parts[0].content, _FULL_OUTPUT)
