from django.test import SimpleTestCase

from hexa.assistant.evals.core.dataset import load_dataset
from hexa.assistant.evals.fixtures import webapp_files
from hexa.assistant.evals.suites import get_suite
from hexa.assistant.evals.suites.webapp_edit.evaluators import ProposalChecks
from hexa.assistant.evals.suites.webapp_edit.schemas import (
    FileCheck,
    ProposedWebappVersion,
    WebappEditInput,
    WebappEditMetadata,
)

# A correct edit per task, as (path, old, new) replacements on the seeded files.
# Proves each case can be passed, not only failed.
SOLUTIONS = {
    "confirmed_line_color": [
        ("js/app.js", "confirmed: '#2563eb'", "confirmed: '#b91c1c'")
    ],
    "header_date_format": [
        (
            "js/app.js",
            "return `${year}-${month}-${day}`;",
            "return `${day}/${month}/${year}`;",
        )
    ],
    "export_csv_french": [
        ("js/i18n.js", "  fr: {\n", "  fr: {\n    export_csv: 'Exporter en CSV',\n")
    ],
    "low_stock_threshold": [
        ("index.html", "LOW_STOCK_THRESHOLD = 20", "LOW_STOCK_THRESHOLD = 50")
    ],
    "last_updated_column": [
        (
            "index.html",
            "<th>Status</th>",
            "<th>Status</th>\n            <th>Last updated</th>",
        ),
        (
            "index.html",
            "${status}</span></td>`;",
            '${status}</span></td>\n            <td class="cell">${item.updated_at}</td>`;',
        ),
    ],
    "rename_title": [
        ("index.html", "Stock Tracker", "Essential Medicines Stock"),
        ("README.md", "Stock Tracker", "Essential Medicines Stock"),
    ],
    "closed_marker_grey": [("js/map.js", "closed: '#dc2626'", "closed: '#9ca3af'")],
    "fix_coordinates": [
        ("js/data.js", "lat: 41.89, lon: -5.27", "lat: 14.89, lon: 5.27")
    ],
    "popup_phone": [
        (
            "js/map.js",
            "Status: ${facility.status}`;",
            "Status: ${facility.status}"
            "${facility.phone ? `<br />${facility.phone}` : ''}`;",
        )
    ],
}


def _evaluate(inputs, metadata, output):
    ctx = type("Ctx", (), {"inputs": inputs, "metadata": metadata, "output": output})()
    return ProposalChecks().evaluate(ctx)


def _apply(files: dict[str, str], edits) -> dict[str, str]:
    files = dict(files)
    for path, old, new in edits:
        assert old in files[path], f"{old!r} not in {path}"
        files[path] = files[path].replace(old, new)
    return files


class WebappEditCasesTest(SimpleTestCase):
    """The committed cases are gradeable: a no-op fails, a correct edit passes."""

    CASES = load_dataset(get_suite("webapp_edit")).cases

    def test_every_task_has_a_solution(self):
        self.assertEqual(set(SOLUTIONS), {case.metadata.task_id for case in self.CASES})

    def test_checked_paths_exist_in_the_webapp(self):
        for case in self.CASES:
            files = webapp_files(case.inputs.webapp)
            for check in case.metadata.checks:
                with self.subTest(case=case.name, path=check.path):
                    self.assertIn(check.path, files)

    def test_unchanged_files_fail_every_case(self):
        for case in self.CASES:
            with self.subTest(case=case.name):
                files = webapp_files(case.inputs.webapp)
                metrics = _evaluate(
                    case.inputs, case.metadata, ProposedWebappVersion(files=files)
                )
                self.assertIs(False, metrics["change_landed"].value)

    def test_a_correct_edit_passes_every_case(self):
        for case in self.CASES:
            with self.subTest(case=case.name):
                files = _apply(
                    webapp_files(case.inputs.webapp),
                    SOLUTIONS[case.metadata.task_id],
                )
                metrics = _evaluate(
                    case.inputs, case.metadata, ProposedWebappVersion(files=files)
                )
                self.assertIs(
                    True, metrics["change_landed"].value, metrics["change_landed"]
                )
                self.assertIs(True, metrics["others_preserved"].value)
                self.assertEqual(1.0, metrics["checks_score"].value)


class ProposalChecksTest(SimpleTestCase):
    INPUTS = WebappEditInput(
        prompt="p", fixture_profile="standard_workspace", webapp="stock-tracker"
    )
    METADATA = WebappEditMetadata(
        task_id="t",
        lang="en",
        checks=[
            FileCheck(path="index.html", contains=[r"LOW_STOCK_THRESHOLD\s*=\s*50\b"])
        ],
    )

    def _fixed(self) -> dict[str, str]:
        return _apply(webapp_files("stock-tracker"), SOLUTIONS["low_stock_threshold"])

    def test_no_proposal_fails_every_assertion(self):
        metrics = _evaluate(
            self.INPUTS, self.METADATA, ProposedWebappVersion(rejected_proposals=2)
        )
        for name in (
            "proposed_a_version",
            "change_landed",
            "others_preserved",
            "first_proposal_accepted",
        ):
            with self.subTest(name=name):
                self.assertIs(False, metrics[name].value)
        self.assertEqual(0.0, metrics["checks_score"].value)

    def test_touching_another_file_is_flagged(self):
        files = self._fixed()
        files["README.md"] += "\nEdited.\n"
        metrics = _evaluate(
            self.INPUTS, self.METADATA, ProposedWebappVersion(files=files)
        )
        self.assertIs(True, metrics["change_landed"].value)
        self.assertIs(False, metrics["others_preserved"].value)
        self.assertIn("README.md", metrics["others_preserved"].reason)

    def test_deleting_a_file_is_flagged(self):
        files = self._fixed()
        del files["README.md"]
        metrics = _evaluate(
            self.INPUTS, self.METADATA, ProposedWebappVersion(files=files)
        )
        self.assertIs(False, metrics["others_preserved"].value)

    def test_a_rejected_first_attempt_is_recorded(self):
        metrics = _evaluate(
            self.INPUTS,
            self.METADATA,
            ProposedWebappVersion(files=self._fixed(), rejected_proposals=1),
        )
        self.assertIs(True, metrics["change_landed"].value)
        self.assertIs(False, metrics["first_proposal_accepted"].value)

    def test_unknown_webapp_fails_on_load(self):
        with self.assertRaises(ValueError):
            WebappEditInput(
                prompt="p", fixture_profile="standard_workspace", webapp="nope"
            )
