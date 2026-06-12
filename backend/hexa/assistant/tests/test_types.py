from pydantic import ValidationError

from hexa.assistant.types import MessageSegmentAdapter, TextSegment, ToolSegment
from hexa.core.test import TestCase


class TextSegmentTest(TestCase):
    def test_serialization(self):
        seg = TextSegment(content="hello")
        self.assertEqual(seg.model_dump(), {"type": "text", "content": "hello"})

    def test_type_field_is_always_text(self):
        seg = TextSegment(content="x")
        self.assertEqual(seg.type, "text")


class ToolSegmentTest(TestCase):
    def test_serialization(self):
        seg = ToolSegment(tool_call_id="call_123")
        self.assertEqual(seg.model_dump(), {"type": "tool", "tool_call_id": "call_123"})

    def test_type_field_is_always_tool(self):
        seg = ToolSegment(tool_call_id="x")
        self.assertEqual(seg.type, "tool")


class MessageSegmentAdapterTest(TestCase):
    def test_parses_text_segment(self):
        result = MessageSegmentAdapter.validate_python(
            [{"type": "text", "content": "hello"}]
        )
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TextSegment)
        self.assertEqual(result[0].content, "hello")

    def test_parses_tool_segment(self):
        result = MessageSegmentAdapter.validate_python(
            [{"type": "tool", "tool_call_id": "call_abc"}]
        )
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ToolSegment)
        self.assertEqual(result[0].tool_call_id, "call_abc")

    def test_parses_mixed_list(self):
        result = MessageSegmentAdapter.validate_python(
            [
                {"type": "text", "content": "I'll run that."},
                {"type": "tool", "tool_call_id": "call_1"},
                {"type": "text", "content": "Done."},
            ]
        )
        self.assertIsInstance(result[0], TextSegment)
        self.assertIsInstance(result[1], ToolSegment)
        self.assertIsInstance(result[2], TextSegment)

    def test_rejects_unknown_type(self):
        with self.assertRaises(ValidationError):
            MessageSegmentAdapter.validate_python([{"type": "unknown", "content": "x"}])

    def test_empty_list(self):
        result = MessageSegmentAdapter.validate_python([])
        self.assertEqual(result, [])

    def test_roundtrip_through_model_dump(self):
        segments = [
            TextSegment(content="hello"),
            ToolSegment(tool_call_id="call_1"),
        ]
        dumped = [s.model_dump() for s in segments]
        restored = MessageSegmentAdapter.validate_python(dumped)
        self.assertIsInstance(restored[0], TextSegment)
        self.assertIsInstance(restored[1], ToolSegment)
