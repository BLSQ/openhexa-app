from django.db import models
from django.test import SimpleTestCase

from hexa.mcp.protocol import _get_tool_schema, get_tools_list
from hexa.mcp.tools.pipelines import create_pipeline
from hexa.mcp.tools.webapps import create_static_webapp, get_static_webapp_file
from hexa.pipelines.models import PipelineFunctionalType
from hexa.webapps.models import Webapp


class _Color(models.TextChoices):
    RED = "red", "Red"
    GREEN = "green", "Green"


class _Priority(models.IntegerChoices):
    LOW = 1, "Low"
    HIGH = 2, "High"


def _sample_tool(
    user,
    name: str,
    start_line: int | None = None,
    page: int = 1,
    ratio: float = 1.0,
    color: _Color = _Color.RED,
    priority: _Priority | None = None,
):
    pass


def _list_tool(
    user,
    tags: list[str],
    counts: list[int],
    ratios: list[float],
    flags: list[bool],
    colors: list[_Color],
    optional_tags: list[str] | None = None,
    mapping: dict[str, int] = None,
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

    def test_text_choices_is_string_enum(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertEqual(
            schema["properties"]["color"],
            {"type": "string", "enum": ["red", "green"]},
        )

    def test_integer_choices_is_integer_enum(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertEqual(
            schema["properties"]["priority"],
            {"type": "integer", "enum": [1, 2]},
        )

    def test_optional_enum_is_not_required(self):
        schema = _get_tool_schema(_sample_tool)
        self.assertNotIn("priority", schema["required"])

    def test_list_generics_become_typed_arrays(self):
        properties = _get_tool_schema(_list_tool)["properties"]
        self.assertEqual(
            properties["tags"], {"type": "array", "items": {"type": "string"}}
        )
        self.assertEqual(
            properties["counts"], {"type": "array", "items": {"type": "integer"}}
        )
        self.assertEqual(
            properties["ratios"], {"type": "array", "items": {"type": "number"}}
        )
        self.assertEqual(
            properties["flags"], {"type": "array", "items": {"type": "boolean"}}
        )

    def test_optional_list_is_unwrapped_to_array(self):
        properties = _get_tool_schema(_list_tool)["properties"]
        self.assertEqual(
            properties["optional_tags"], {"type": "array", "items": {"type": "string"}}
        )

    def test_list_of_enum_is_array_of_enum(self):
        properties = _get_tool_schema(_list_tool)["properties"]
        self.assertEqual(
            properties["colors"],
            {"type": "array", "items": {"type": "string", "enum": ["red", "green"]}},
        )

    def test_non_list_generic_falls_back_to_string(self):
        properties = _get_tool_schema(_list_tool)["properties"]
        self.assertEqual(properties["mapping"]["type"], "string")

    def test_create_pipeline_functional_type_exposes_graphql_values(self):
        schema = _get_tool_schema(create_pipeline)
        prop = schema["properties"]["functional_type"]
        self.assertEqual(prop["type"], "string")
        self.assertEqual(set(prop["enum"]), {c.value for c in PipelineFunctionalType})
        self.assertIn("extraction", prop["enum"])
        self.assertNotIn("functional_type", schema["required"])


class ToolsListTest(SimpleTestCase):
    def test_create_pipeline_advertises_functional_type_enum(self):
        tools = {t["name"]: t for t in get_tools_list()}
        self.assertIn("create_pipeline", tools)
        prop = tools["create_pipeline"]["inputSchema"]["properties"]["functional_type"]
        self.assertEqual(prop["type"], "string")
        self.assertEqual(set(prop["enum"]), {c.value for c in PipelineFunctionalType})

    def test_create_static_webapp_advertises_allowed_operations_enum(self):
        schema = _get_tool_schema(create_static_webapp)
        prop = schema["properties"]["allowed_operations"]
        self.assertEqual(prop["type"], "array")
        self.assertEqual(prop["items"]["type"], "string")
        self.assertEqual(
            set(prop["items"]["enum"]), {c.value for c in Webapp.OperationScope}
        )
        self.assertIn("PIPELINES_READ", prop["items"]["enum"])
        self.assertNotIn("allowed_operations", schema["required"])
