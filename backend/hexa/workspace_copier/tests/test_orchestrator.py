from unittest.mock import patch

from django.test import SimpleTestCase

from hexa.workspace_copier import orchestrator
from hexa.workspace_copier.orchestrator import (
    WORKSPACE_COPIERS,
    _resolve_selection,
    copy_workspace,
)
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.base import ResourceCopier


class FakeCopier(ResourceCopier):
    def __init__(self, name, *, mandatory=False, depends_on=()):
        self.name = name
        self.label = name
        self.mandatory = mandatory
        self.depends_on = depends_on
        self.calls = []

    def copy(self, source, target, result, reporter):
        self.calls.append((source, target))
        reporter.info(f"ran:{self.name}")
        result.warn(f"ran:{self.name}")


class ResolveSelectionTest(SimpleTestCase):
    def test_none_selects_all_in_registry_order(self):
        selected = _resolve_selection(WORKSPACE_COPIERS, None)
        self.assertEqual(
            [c.name for c in selected], [c.name for c in WORKSPACE_COPIERS]
        )

    def test_subset_always_includes_mandatory_and_preserves_order(self):
        selected = _resolve_selection(WORKSPACE_COPIERS, {"pipelines"})
        names = [c.name for c in selected]
        self.assertIn("workspace", names)  # mandatory force-included
        self.assertIn("pipelines", names)
        # order matches registry (workspace appears before pipelines)
        self.assertLess(names.index("workspace"), names.index("pipelines"))

    def test_unknown_names_are_ignored(self):
        selected = _resolve_selection(WORKSPACE_COPIERS, {"does-not-exist"})
        self.assertEqual([c.name for c in selected], ["workspace"])


class CopyWorkspaceTest(SimpleTestCase):
    def test_runs_selected_copiers_in_order(self):
        fakes = [
            FakeCopier("workspace", mandatory=True),
            FakeCopier("files"),
            FakeCopier("pipelines", depends_on=("files",)),
        ]
        with patch.object(orchestrator, "WORKSPACE_COPIERS", fakes):
            result = copy_workspace(object(), object(), NullReporter())
        ran = [w for w in result.warnings if w.startswith("ran:")]
        self.assertEqual(ran, ["ran:workspace", "ran:files", "ran:pipelines"])

    def test_warns_when_dependency_deselected(self):
        fakes = [
            FakeCopier("workspace", mandatory=True),
            FakeCopier("files"),
            FakeCopier("pipelines", depends_on=("files",)),
        ]
        with patch.object(orchestrator, "WORKSPACE_COPIERS", fakes):
            result = copy_workspace(
                object(), object(), NullReporter(), resources={"pipelines"}
            )
        self.assertTrue(
            any("dependency 'files' not selected" in w for w in result.warnings)
        )
        # files copier did not run
        self.assertFalse(fakes[1].calls)

    def test_no_warning_when_dependency_selected(self):
        fakes = [
            FakeCopier("workspace", mandatory=True),
            FakeCopier("files"),
            FakeCopier("pipelines", depends_on=("files",)),
        ]
        with patch.object(orchestrator, "WORKSPACE_COPIERS", fakes):
            result = copy_workspace(
                object(), object(), NullReporter(), resources={"files", "pipelines"}
            )
        self.assertFalse(any("not selected" in w for w in result.warnings))
