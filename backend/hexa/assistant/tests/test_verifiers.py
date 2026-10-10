from django.test import SimpleTestCase

from hexa.assistant.evals.verifiers import ASSERTION_TIERS, WorldSpec, run_verifiers
from hexa.assistant.evals.verifiers.common import symbols
from hexa.assistant.evals.verifiers.pipelines.best_practices import RULES

WORLD = WorldSpec(
    connection_slugs=frozenset(
        {"dhis2-play", "dhis2-target", "iaso-staging", "cds-climate"}
    ),
    dataset_slugs=frozenset({"boundaries"}),
    file_paths=frozenset({"data/mapping.csv"}),
)

# Negative controls: correct OpenHEXA idiom that must never be flagged. These
# stand in for the template-calibration corpus - a rule strict enough to
# condemn code written this way is a broken rule.
GOOD_MINIMAL = '''
from openhexa.sdk import current_run, pipeline


@pipeline("hello")
def hello():
    """A minimal pipeline."""
    current_run.log_info("done")
'''

GOOD_CONNECTION_AND_WIDGET = '''
from pathlib import Path

from openhexa.sdk import (
    DHIS2Connection,
    DHIS2Widget,
    current_run,
    parameter,
    pipeline,
    workspace,
)


@pipeline("dhis2_shapes_extract")
@parameter("dhis2_connection", type=DHIS2Connection, required=True)
@parameter(
    "org_unit_level",
    type=str,
    widget=DHIS2Widget.ORG_UNIT_LEVELS,
    connection="dhis2_connection",
    required=False,
    default=None,
)
def dhis2_shapes_extract(dhis2_connection, org_unit_level=None):
    """Extract org unit shapes."""
    output_path = Path(workspace.files_path) / "pipelines" / "shapes"
    current_run.log_info(f"Writing shapes to {output_path}")
    current_run.add_file_output(output_path.as_posix())
'''

GOOD_TOOLBOX = '''
from openhexa.sdk import current_run, pipeline, workspace
from openhexa.toolbox.dhis2 import DHIS2


@pipeline("dhis2_metadata")
def dhis2_metadata():
    """Extract metadata via the toolbox."""
    connection = workspace.dhis2_connection("dhis2-play")
    client = DHIS2(connection)
    current_run.log_info(f"connected to {client}")
'''

GOOD_PIPELINES = {
    "minimal": GOOD_MINIMAL,
    "connection_and_widget": GOOD_CONNECTION_AND_WIDGET,
    "toolbox": GOOD_TOOLBOX,
}


def files(pipeline_source: str, **extra: str) -> dict[str, str]:
    return {"pipeline.py": pipeline_source, **extra}


class KnownGoodPipelinesTest(SimpleTestCase):
    def test_known_good_pipelines_score_clean(self):
        for name, source in GOOD_PIPELINES.items():
            with self.subTest(pipeline=name):
                report = run_verifiers(files(source), WORLD)
                self.assertEqual(
                    [],
                    report.findings,
                    f"{name} was flagged: {[f.message for f in report.findings]}",
                )
                self.assertEqual(1.0, report.average_score)


class ValidPipelineTest(SimpleTestCase):
    def test_missing_pipeline_file(self):
        report = run_verifiers({"helpers.py": "x = 1"}, WORLD)
        self.assertFalse(report.tiers["valid_pipeline"].passed)
        self.assertEqual("pipeline_file_missing", report.findings[0].rule)

    def test_no_pipeline_decorator(self):
        report = run_verifiers(files("def run():\n    pass\n"), WORLD)
        self.assertFalse(report.tiers["valid_pipeline"].passed)
        self.assertEqual(
            "pipeline_not_found", report.tiers["valid_pipeline"].findings[0].rule
        )

    def test_widget_without_connection_is_rejected(self):
        source = '''
from openhexa.sdk import DHIS2Widget, parameter, pipeline


@pipeline("broken")
@parameter("org_units", type=str, widget=DHIS2Widget.ORG_UNITS)
def broken(org_units):
    """Widget with no connection parameter."""
'''
        report = run_verifiers(files(source), WORLD)
        self.assertFalse(report.tiers["valid_pipeline"].passed)
        self.assertEqual(
            "invalid_parameter", report.tiers["valid_pipeline"].findings[0].rule
        )

    def test_connection_field_referencing_unknown_parameter(self):
        source = '''
from openhexa.sdk import DHIS2Widget, parameter, pipeline


@pipeline("broken")
@parameter("org_units", type=str, widget=DHIS2Widget.ORG_UNITS, connection="nope")
def broken(org_units):
    """Connection field points at a parameter that does not exist."""
'''
        report = run_verifiers(files(source), WORLD)
        self.assertFalse(report.tiers["valid_pipeline"].passed)

    def test_syntax_error(self):
        report = run_verifiers(files("def broken(:\n"), WORLD)
        self.assertFalse(report.tiers["valid_pipeline"].passed)
        self.assertEqual(0.0, report.tiers["valid_pipeline"].score)


class ValidSdkUseTest(SimpleTestCase):
    def test_hallucinated_workspace_attribute(self):
        source = '''
from openhexa.sdk import pipeline, workspace


@pipeline("bad")
def bad():
    """workspace.files does not exist."""
    return workspace.files.read("a.csv")
'''
        report = run_verifiers(files(source), WORLD)
        rules = {f.rule for f in report.tiers["valid_sdk_use"].findings}
        self.assertIn("unknown_attribute", rules)
        self.assertLess(report.tiers["valid_sdk_use"].score, 1.0)

    def test_hallucinated_import(self):
        source = '''
from openhexa.sdk import magic_helper, pipeline


@pipeline("bad")
def bad():
    """Imports a symbol that does not exist."""
    magic_helper()
'''
        report = run_verifiers(files(source), WORLD)
        findings = report.tiers["valid_sdk_use"].findings
        self.assertEqual(["unknown_symbol"], [f.rule for f in findings])
        self.assertEqual(
            1, report.tiers["valid_sdk_use"].counts["hallucinated_symbols"]
        )

    def test_unknown_module(self):
        source = '''
from openhexa.sdk.nonexistent import thing
from openhexa.sdk import pipeline


@pipeline("bad")
def bad():
    """Imports a module that does not exist."""
    thing()
'''
        report = run_verifiers(files(source), WORLD)
        self.assertIn(
            "unknown_module", {f.rule for f in report.tiers["valid_sdk_use"].findings}
        )

    def test_current_run_typo(self):
        source = '''
from openhexa.sdk import current_run, pipeline


@pipeline("bad")
def bad():
    """log_information is not a real method."""
    current_run.log_information("hi")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertIn(
            "unknown_attribute",
            {f.rule for f in report.tiers["valid_sdk_use"].findings},
        )


class GroundingTest(SimpleTestCase):
    def test_unknown_connection_slug(self):
        source = '''
from openhexa.sdk import pipeline, workspace


@pipeline("bad")
def bad():
    """Invents a connection identifier."""
    return workspace.dhis2_connection("dhis2-prod-kenya")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertEqual(
            ["unknown_connection"], [f.rule for f in report.tiers["grounding"].findings]
        )
        self.assertEqual(0.0, report.tiers["grounding"].score)

    def test_known_connection_slug(self):
        source = '''
from openhexa.sdk import pipeline, workspace


@pipeline("ok")
def ok():
    """Uses a seeded connection."""
    return workspace.dhis2_connection("dhis2-play")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertEqual([], report.tiers["grounding"].findings)

    def test_parameter_supplied_connection_is_not_penalised(self):
        source = '''
from openhexa.sdk import pipeline, workspace


@pipeline("ok")
def ok(slug):
    """A non-literal identifier cannot be resolved statically."""
    return workspace.dhis2_connection(slug)
'''
        report = run_verifiers(files(source), WORLD)
        self.assertEqual([], report.tiers["grounding"].findings)
        self.assertEqual(
            0, report.tiers["grounding"].counts["grounded_references_checked"]
        )

    def test_unknown_dataset(self):
        source = '''
from openhexa.sdk import pipeline, workspace


@pipeline("bad")
def bad():
    """Invents a dataset."""
    return workspace.get_dataset("not-a-dataset")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertEqual(
            ["unknown_dataset"], [f.rule for f in report.tiers["grounding"].findings]
        )


class BestPracticesTest(SimpleTestCase):
    def test_print_instead_of_log(self):
        source = '''
from openhexa.sdk import pipeline


@pipeline("bad")
def bad():
    """Prints instead of logging."""
    print("hello")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertIn(
            "no_print", {f.rule for f in report.tiers["best_practices"].findings}
        )
        # Expressed against the rule count so adding a rule does not require
        # editing this assertion - only the denominator moves.
        self.assertAlmostEqual(
            (len(RULES) - 1) / len(RULES), report.tiers["best_practices"].score
        )

    def test_env_credentials(self):
        source = '''
import os

from openhexa.sdk import pipeline


@pipeline("bad")
def bad():
    """Reads credentials from the environment."""
    return os.getenv("DHIS2_PASSWORD")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertIn(
            "no_env_credentials",
            {f.rule for f in report.tiers["best_practices"].findings},
        )

    def _rules(self, body: str) -> set[str]:
        source = (
            "from openhexa.sdk import pipeline, workspace\n\n\n"
            '@pipeline("p")\n'
            "def p():\n"
            '    """Doc."""\n' + body
        )
        return {f.rule for f in run_verifiers(files(source), WORLD).findings}

    def test_hardcoded_files_path(self):
        self.assertIn(
            "no_hardcoded_workspace_path",
            self._rules('    p = "/home/hexa/workspace/data.csv"\n'),
        )

    def test_hardcoded_tmp_path(self):
        self.assertIn(
            "no_hardcoded_workspace_path",
            self._rules('    p = "/home/hexa/tmp/scratch.csv"\n'),
        )

    def test_unrelated_home_path_is_not_a_workspace_mistake(self):
        """Only the paths the SDK accessors resolve to are the anti-pattern."""
        self.assertNotIn(
            "no_hardcoded_workspace_path",
            self._rules('    p = "/home/someone/notes.txt"\n'),
        )

    def test_paths_openhexa_does_not_use_are_not_flagged(self):
        """/srv, /mnt and /workspace were guesses; none appear in real pipelines."""
        for path in ("/srv/data.csv", "/mnt/data.csv", "/workspace/data.csv"):
            with self.subTest(path=path):
                self.assertNotIn(
                    "no_hardcoded_workspace_path", self._rules(f'    p = "{path}"\n')
                )

    def test_path_built_from_the_accessor_is_clean(self):
        self.assertNotIn(
            "no_hardcoded_workspace_path",
            self._rules('    p = f"{workspace.files_path}/out.csv"\n'),
        )

    def test_raw_http_against_dhis2(self):
        source = '''
import requests

from openhexa.sdk import DHIS2Connection, parameter, pipeline


@pipeline("bad")
@parameter("con", type=DHIS2Connection)
def bad(con):
    """Bypasses the toolbox."""
    return requests.get(f"{con.url}/api/dataValueSets.json")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertIn(
            "use_toolbox_not_http",
            {f.rule for f in report.tiers["best_practices"].findings},
        )

    def test_unregistered_output(self):
        source = '''
import polars as pl

from openhexa.sdk import pipeline, workspace


@pipeline("bad")
def bad():
    """Writes a file but never registers it."""
    pl.DataFrame().write_csv(f"{workspace.files_path}/out.csv")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertIn(
            "register_outputs",
            {f.rule for f in report.tiers["best_practices"].findings},
        )

    def test_registered_output_is_clean(self):
        source = '''
import polars as pl

from openhexa.sdk import current_run, pipeline, workspace


@pipeline("ok")
def ok():
    """Writes and registers."""
    path = f"{workspace.files_path}/out.csv"
    pl.DataFrame().write_csv(path)
    current_run.add_file_output(path)
'''
        report = run_verifiers(files(source), WORLD)
        self.assertEqual([], report.tiers["best_practices"].findings)
        self.assertEqual(1.0, report.tiers["best_practices"].score)


class HardcodedSecretsTest(SimpleTestCase):
    """Detection is by NAME, never by the shape of the literal.

    Entropy or length heuristics are unusable here: DHIS2 UIDs such as
    "HllvX50cXC0" are indistinguishable from API keys, and real pipelines are
    full of them.
    """

    def _rules(self, body: str) -> set[str]:
        source = (
            "from openhexa.sdk import pipeline\n\n\n"
            '@pipeline("p")\n'
            "def p():\n"
            '    """Doc."""\n' + body
        )
        return {f.rule for f in run_verifiers(files(source), WORLD).findings}

    def test_assigned_password(self):
        self.assertIn("no_hardcoded_secrets", self._rules('    password = "hunter2"\n'))

    def test_assigned_api_key_variants(self):
        for name in ("api_key", "apikey", "ACCESS_KEY", "dhis2_token", "my_secret"):
            with self.subTest(name=name):
                self.assertIn(
                    "no_hardcoded_secrets", self._rules(f'    {name} = "abc123"\n')
                )

    def test_keyword_argument(self):
        self.assertIn(
            "no_hardcoded_secrets", self._rules('    connect(password="hunter2")\n')
        )

    def test_dict_literal(self):
        self.assertIn(
            "no_hardcoded_secrets", self._rules('    cfg = {"api_key": "abc123"}\n')
        )

    def test_known_credential_prefix_regardless_of_name(self):
        self.assertIn("no_hardcoded_secrets", self._rules('    x = "sk-abc123def"\n'))

    def test_dhis2_uid_is_not_a_secret(self):
        """The false positive that rules out entropy-based detection."""
        self.assertNotIn(
            "no_hardcoded_secrets", self._rules('    de = "HllvX50cXC0"\n')
        )

    def test_parameter_supplied_credential_is_clean(self):
        """The idiomatic form: the value is not a literal."""
        self.assertNotIn(
            "no_hardcoded_secrets",
            self._rules("    password = connection.password\n"),
        )

    def test_empty_literal_is_not_flagged(self):
        self.assertNotIn("no_hardcoded_secrets", self._rules('    password = ""\n'))

    def test_the_secret_value_is_never_echoed(self):
        """Findings reach Logfire; a real key must not travel with them."""
        source = (
            "from openhexa.sdk import pipeline\n\n\n"
            '@pipeline("p")\n'
            "def p():\n"
            '    """Doc."""\n'
            '    password = "sup3rs3cr3t"\n'
        )
        report = run_verifiers(files(source), WORLD)
        blob = " ".join(f.message for f in report.findings)
        blob += report.metrics()["best_practices_score"].note
        self.assertNotIn("sup3rs3cr3t", blob)
        self.assertIn("11-character", blob)


class ReportTest(SimpleTestCase):
    def test_metrics_shape(self):
        report = run_verifiers(files(GOOD_MINIMAL), WORLD)
        metrics = report.metrics()
        self.assertEqual(
            {
                "valid_pipeline_score",
                "valid_sdk_use_score",
                "grounding_score",
                "best_practices_score",
                "average_score",
                "valid_pipeline_passed",
                "valid_sdk_use_passed",
                "grounding_passed",
            },
            set(metrics),
            "the reported metric surface changed",
        )
        self.assertIs(True, metrics["valid_pipeline_passed"].value)
        self.assertIs(True, metrics["valid_sdk_use_passed"].value)

    def test_grounding_assertion_fails_on_an_invented_identifier(self):
        source = '''
from openhexa.sdk import pipeline, workspace


@pipeline("bad")
def bad():
    """Invents a connection identifier."""
    return workspace.dhis2_connection("dhis2-prod-kenya")
'''
        metrics = run_verifiers(files(source), WORLD).metrics()
        self.assertIs(False, metrics["grounding_passed"].value)
        # The API itself is real, so SDK use passes - the two are independent.
        self.assertIs(True, metrics["valid_sdk_use_passed"].value)

    def test_grounding_assertion_passes_when_identifiers_are_parameters(self):
        """Not inventing an identifier is a pass, even with nothing to check."""
        source = '''
from openhexa.sdk import pipeline, workspace


@pipeline("ok")
def ok(slug):
    """The idiomatic form: the identifier comes from a parameter."""
    return workspace.dhis2_connection(slug)
'''
        metrics = run_verifiers(files(source), WORLD).metrics()
        self.assertIs(True, metrics["grounding_passed"].value)
        self.assertIn("came from parameters", metrics["grounding_passed"].note)

    def test_every_metric_carries_a_note(self):
        """The retired count metrics live here now; an empty note loses them."""
        for name, metric in run_verifiers(files(GOOD_MINIMAL), WORLD).metrics().items():
            with self.subTest(metric=name):
                self.assertTrue(metric.note, f"{name} has no note")

    def test_notes_carry_the_denominators(self):
        metrics = run_verifiers(files(GOOD_CONNECTION_AND_WIDGET), WORLD).metrics()
        self.assertIn("symbol(s) checked", metrics["valid_sdk_use_score"].note)
        self.assertIn("reference(s) checked", metrics["grounding_score"].note)
        self.assertIn("rules triggered", metrics["best_practices_score"].note)

    def test_every_assertion_tier_emits_a_boolean(self):
        metrics = run_verifiers(files(GOOD_MINIMAL), WORLD).metrics()
        for tier in ASSERTION_TIERS:
            with self.subTest(tier=tier):
                self.assertIsInstance(metrics[f"{tier}_passed"].value, bool)

    def test_valid_sdk_use_assertion_fails_on_a_hallucinated_symbol(self):
        source = '''
from openhexa.sdk import magic_helper, pipeline


@pipeline("bad")
def bad():
    """Imports a symbol that does not exist."""
    magic_helper()
'''
        metrics = run_verifiers(files(source), WORLD).metrics()
        self.assertIs(False, metrics["valid_sdk_use_passed"].value)
        # The pipeline itself is still structurally valid - the two assertions
        # are independent, which is the point of reporting both.
        self.assertIs(True, metrics["valid_pipeline_passed"].value)

    def test_valid_pipeline_assertion_fails_independently_of_sdk_use(self):
        source = '''
from openhexa.sdk import current_run, pipeline


def bad():
    """No @pipeline decorator, but every symbol is real."""
    current_run.log_info("hi")
'''
        metrics = run_verifiers(files(source), WORLD).metrics()
        self.assertIs(False, metrics["valid_pipeline_passed"].value)
        self.assertIs(True, metrics["valid_sdk_use_passed"].value)

    def test_empty_pipeline_passes_every_deterministic_tier(self):
        """The gap tier 4 exists to close: a no-op is perfectly conformant."""
        source = '''
from openhexa.sdk import pipeline


@pipeline("empty")
def empty():
    """Does nothing at all."""
'''
        report = run_verifiers(files(source), WORLD)
        self.assertEqual([], report.findings)
        self.assertEqual(1.0, report.average_score)


class RealWorldBestPracticesTest(SimpleTestCase):
    """Patterns found in shipped OpenHEXA templates that must not be flagged."""

    def test_urllib_parse_is_not_an_http_call(self):
        source = '''
from urllib.parse import urlparse

from openhexa.sdk import DHIS2Connection, parameter, pipeline


@pipeline("ok")
@parameter("con", type=DHIS2Connection)
def ok(con):
    """Parsing a URL is not hand-rolled API access."""
    return urlparse(con.url).netloc
'''
        report = run_verifiers(files(source), WORLD)
        self.assertNotIn(
            "use_toolbox_not_http",
            {f.rule for f in report.tiers["best_practices"].findings},
        )

    def test_dataset_version_publishing_counts_as_registration(self):
        source = '''
import polars as pl

from openhexa.sdk import Dataset, parameter, pipeline, workspace


@pipeline("ok")
@parameter("dataset", type=Dataset)
def ok(dataset):
    """Publishes through the dataset API rather than add_file_output."""
    path = f"{workspace.files_path}/out.csv"
    pl.DataFrame().write_csv(path)
    version = dataset.create_version(name="v1")
    version.add_file(source=path, filename="out.csv")
'''
        report = run_verifiers(files(source), WORLD)
        self.assertNotIn(
            "register_outputs",
            {f.rule for f in report.tiers["best_practices"].findings},
        )

    def test_head_probe_is_not_hand_rolled_api_access(self):
        source = '''
import requests

from openhexa.sdk import DHIS2Connection, parameter, pipeline


@pipeline("ok")
@parameter("con", type=DHIS2Connection)
def ok(con):
    """A reachability probe has no toolbox equivalent."""
    return requests.head(con.url).status_code
'''
        report = run_verifiers(files(source), WORLD)
        self.assertNotIn(
            "use_toolbox_not_http",
            {f.rule for f in report.tiers["best_practices"].findings},
        )


class ModuleStatusTest(SimpleTestCase):
    def test_missing_module(self):
        self.assertIs(False, symbols.module_exists("openhexa.sdk.definitely_not_here"))

    def test_installed_module(self):
        self.assertIs(True, symbols.module_exists("openhexa.sdk"))

    def test_non_openhexa_module_is_refused(self):
        with self.assertRaises(ValueError):
            symbols.module_status("os")

    def test_unimportable_module_is_unverifiable_not_missing(self):
        """A module whose own dependency is absent must not read as a hallucination.

        `openhexa.toolbox.era5.extract` exists but needs xarray, which the app
        image does not install - reporting it as unknown would blame the agent
        for this image's dependency set.
        """
        if (
            symbols.module_status("openhexa.toolbox.era5.extract")
            is not symbols.ModuleStatus.UNIMPORTABLE
        ):
            self.skipTest("era5.extract is importable in this environment")
        self.assertIsNone(symbols.module_exists("openhexa.toolbox.era5.extract"))
        source = '''
from openhexa.sdk import pipeline
from openhexa.toolbox.era5.extract import ERA5


@pipeline("ok")
def ok():
    """Imports a module this image cannot load."""
    return ERA5
'''
        report = run_verifiers(files(source), WORLD)
        self.assertEqual([], report.tiers["valid_sdk_use"].findings)
