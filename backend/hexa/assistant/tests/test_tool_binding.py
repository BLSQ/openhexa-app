import inspect
from unittest import TestCase

from hexa.assistant.tool_binding import bind_context


def _sample_func(user, workspace_slug: str, name: str) -> str:
    """Sample function docstring."""
    return f"{user}:{workspace_slug}:{name}"


def _no_context_func(name: str, value: int) -> str:
    """No context params."""
    return f"{name}={value}"


class BindContextTest(TestCase):
    def test_injects_matching_context_keys(self):
        bound = bind_context(_sample_func, {"user": "alice", "workspace_slug": "ws-1"})
        self.assertEqual(bound(name="pipeline"), "alice:ws-1:pipeline")

    def test_ignores_nonmatching_context_keys(self):
        bound = bind_context(
            _sample_func,
            {"user": "alice", "workspace_slug": "ws-1", "extra": "ignored"},
        )
        self.assertEqual(bound(name="test"), "alice:ws-1:test")

    def test_removes_bound_params_from_signature(self):
        bound = bind_context(_sample_func, {"user": "alice", "workspace_slug": "ws-1"})
        params = list(inspect.signature(bound).parameters.keys())
        self.assertNotIn("user", params)
        self.assertNotIn("workspace_slug", params)
        self.assertIn("name", params)

    def test_preserves_unbound_params_in_signature(self):
        bound = bind_context(_sample_func, {"user": "alice"})
        params = list(inspect.signature(bound).parameters.keys())
        self.assertIn("workspace_slug", params)
        self.assertIn("name", params)
        self.assertNotIn("user", params)

    def test_preserves_name_qualname_and_docstring(self):
        bound = bind_context(_sample_func, {"user": "alice"})
        self.assertEqual(bound.__name__, "_sample_func")
        self.assertEqual(bound.__qualname__, _sample_func.__qualname__)
        self.assertEqual(bound.__doc__, "Sample function docstring.")

    def test_returns_original_when_no_context_keys_match(self):
        result = bind_context(
            _no_context_func, {"user": "alice", "workspace_slug": "ws-1"}
        )
        self.assertIs(result, _no_context_func)

    def test_returns_original_with_empty_context(self):
        result = bind_context(_sample_func, {})
        self.assertIs(result, _sample_func)
