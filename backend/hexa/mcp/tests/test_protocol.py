from django.test import SimpleTestCase

from hexa.mcp.protocol import _get_tool_schema
from hexa.mcp.tools.webapps import get_static_webapp_file


def _sample_tool(
    user,
    name: str,
    start_line: int | None = None,
    page: int = 1,
    ratio: float = 1.0,
):
    pass


class ToolSchemaTest(SimpleTestCase):
    def test_optional_int_is_advertised_as_integer(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertEqual(schema["properties"]["start_line"]["type"], "integer")
        self.assertEqual(schema["properties"]["page"]["type"], "integer")
        self.assertEqual(schema["properties"]["ratio"]["type"], "number")
        self.assertEqual(schema["properties"]["name"]["type"], "string")

    def test_user_arg_is_excluded(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertNotIn("user", schema["properties"])

    def test_required_are_args_without_defaults(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertEqual(schema["required"], ["name"])

    def test_optional_int_arg_is_not_required(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertNotIn("start_line", schema["required"])

    def test_webapp_file_line_range_is_optional_integer(self):
        schema = _get_tool_schema(get_static_webapp_file)
        for arg in ("start_line", "end_line"):
            self.assertEqual(schema["properties"][arg]["type"], "integer")
            self.assertNotIn(arg, schema["required"])
        self.assertEqual(schema["required"], ["workspace_slug", "webapp_slug", "path"])
