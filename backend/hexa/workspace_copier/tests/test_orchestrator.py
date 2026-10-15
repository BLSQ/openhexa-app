from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from hexa.workspace_copier import orchestrator
from hexa.workspace_copier.endpoints import Endpoint
from hexa.workspace_copier.options import CopyOptions
from hexa.workspace_copier.orchestrator import (
    WORKSPACE_COPIERS,
    _resolve_selection,
    copy_workspace,
)
from hexa.workspace_copier.progress import NullReporter
from hexa.workspace_copier.resources.base import ResourceCopier
from hexa.workspace_copier.results import CopyResult


class FakeCopier(ResourceCopier):
    def __init__(self, name, *, mandatory=False, depends_on=(), supports_local=False):
        self.name = name
        self.label = name
        self.mandatory = mandatory
        self.depends_on = depends_on
        self.supports_local = supports_local
        self.calls = []
        self.options = {}

    def copy(self, source, target, result, reporter, *, options=CopyOptions()):
        self.calls.append((source, target))
        self.options = options
        reporter.info(f"ran:{self.name}")
        result.warn(f"ran:{self.name}")


class FailingCopier(FakeCopier):
    def copy(self, source, target, result, reporter, *, options=CopyOptions()):
        raise RuntimeError("boom")


def _remote():
    return Endpoint.remote(MagicMock(), "ws")


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

    def test_registry_order(self):
        self.assertEqual(
            [c.name for c in WORKSPACE_COPIERS],
            [
                "workspace",
                "files",
                "database",
                "connections",
                "pipelines",
                "datasets",
                "webapps",
            ],
        )

    def test_webapps_can_be_selected_alone(self):
        selected = _resolve_selection(WORKSPACE_COPIERS, {"webapps"})
        self.assertEqual([c.name for c in selected], ["workspace", "webapps"])

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
            result = copy_workspace(_remote(), _remote(), NullReporter())
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
                _remote(), _remote(), NullReporter(), resources={"pipelines"}
            )
        self.assertTrue(
            any("dependency 'files' not selected" in w for w in result.warnings)
        )
        # files copier did not run
        self.assertFalse(fakes[1].calls)

    def test_options_reach_every_copier(self):
        fakes = [FakeCopier("workspace", mandatory=True), FakeCopier("datasets")]
        options = CopyOptions(all_dataset_versions=True)
        with patch.object(orchestrator, "WORKSPACE_COPIERS", fakes):
            copy_workspace(_remote(), _remote(), NullReporter(), options=options)
        self.assertTrue(all(f.options is options for f in fakes))

    def test_no_warning_when_dependency_selected(self):
        fakes = [
            FakeCopier("workspace", mandatory=True),
            FakeCopier("files"),
            FakeCopier("pipelines", depends_on=("files",)),
        ]
        with patch.object(orchestrator, "WORKSPACE_COPIERS", fakes):
            result = copy_workspace(
                _remote(), _remote(), NullReporter(), resources={"files", "pipelines"}
            )
        self.assertFalse(any("not selected" in w for w in result.warnings))

    def test_given_result_keeps_progress_when_a_copier_raises(self):
        fakes = [FakeCopier("workspace", mandatory=True), FailingCopier("files")]
        result = CopyResult()
        with (
            patch.object(orchestrator, "WORKSPACE_COPIERS", fakes),
            self.assertRaises(RuntimeError),
        ):
            copy_workspace(_remote(), _remote(), NullReporter(), result=result)
        self.assertIn("ran:workspace", result.warnings)
        self.assertIsNotNone(result.started_at)

    def test_copier_without_local_support_is_skipped_in_a_local_run(self):
        fakes = [
            FakeCopier("workspace", mandatory=True, supports_local=True),
            FakeCopier("files"),
            FakeCopier("webapps", supports_local=True),
        ]
        with patch.object(orchestrator, "WORKSPACE_COPIERS", fakes):
            result = copy_workspace(
                Endpoint.local("src"), Endpoint.local("tgt"), NullReporter()
            )
        ran = [w for w in result.warnings if w.startswith("ran:")]
        self.assertEqual(ran, ["ran:workspace", "ran:webapps"])
        self.assertTrue(any(w.startswith("files: skipped") for w in result.warnings))

    def test_database_copier_runs_in_a_local_run(self):
        database = next(c for c in WORKSPACE_COPIERS if c.name == "database")
        self.assertTrue(database.supports_local)
