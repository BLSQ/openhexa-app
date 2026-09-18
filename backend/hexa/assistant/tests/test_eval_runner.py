import json
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError, OutputWrapper
from django.test import SimpleTestCase
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

from hexa.assistant.evals.core.dataset import (
    DatasetError,
    dataset_hash,
    instructions_hash,
    validate_cases,
)
from hexa.assistant.evals.suites import SUITES, get_suite
from hexa.assistant.evals.suites.pipeline_create.evaluators import (
    Trajectory,
    VerifierScores,
)
from hexa.assistant.evals.suites.pipeline_create.schemas import (
    PipelineCreateInput,
    PipelineCreateMetadata,
    ProposedPipeline,
)
from hexa.assistant.evals.suites.pipeline_create.task import _files_from_args
from hexa.assistant.evals.verifiers import ASSERTION_TIERS
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.management.commands import run_evals
from hexa.assistant.management.commands.run_evals import Command

GOOD_PIPELINE = '''
from openhexa.sdk import current_run, pipeline, workspace


@pipeline("extract")
def extract():
    """Reads a seeded connection."""
    workspace.dhis2_connection("dhis2-play")
    current_run.log_info("done")
'''


def make_case(name: str, profile: str = "standard_workspace", lang: str = "en") -> Case:
    return Case(
        name=name,
        inputs=PipelineCreateInput(
            prompt=f"prompt for {name}", fixture_profile=profile
        ),
        metadata=PipelineCreateMetadata(task_id=name, lang=lang),
    )


def make_dataset(*cases: Case) -> Dataset:
    return Dataset(name="eval-runner-tests", cases=list(cases))


class FilesFromArgsTest(SimpleTestCase):
    def test_parses_the_agents_files_json(self):
        args = {
            "files_json": json.dumps(
                [
                    {"path": "pipeline.py", "content": "x = 1"},
                    {"path": "requirements.txt", "content": "polars"},
                ]
            )
        }
        self.assertEqual(
            {"pipeline.py": "x = 1", "requirements.txt": "polars"},
            _files_from_args(args),
        )

    def test_accepts_an_already_decoded_list(self):
        args = {"files_json": [{"path": "pipeline.py", "content": "x = 1"}]}
        self.assertEqual({"pipeline.py": "x = 1"}, _files_from_args(args))

    def test_malformed_json_yields_no_files(self):
        """Tier 0 should fail this on its own merits, not crash the run."""
        self.assertEqual({}, _files_from_args({"files_json": '[{"path": '}))

    def test_missing_or_wrong_shape_yields_no_files(self):
        self.assertEqual({}, _files_from_args({}))
        self.assertEqual({}, _files_from_args({"files_json": '{"path": "a"}'}))
        self.assertEqual({}, _files_from_args({"files_json": '[{"content": "x"}]'}))


class VerifierScoresEvaluatorTest(SimpleTestCase):
    def _evaluate(self, output: ProposedPipeline) -> dict:
        ctx = type(
            "Ctx",
            (),
            {
                "inputs": PipelineCreateInput(
                    prompt="p", fixture_profile="standard_workspace"
                ),
                "output": output,
                "metadata": PipelineCreateMetadata(task_id="t", lang="en"),
            },
        )()
        return VerifierScores().evaluate(ctx)

    def test_no_files_is_not_a_clean_pass(self):
        """Answering in prose must not score as perfect conformance."""
        metrics = self._evaluate(ProposedPipeline(tool_calls=["get_help_or_doc"]))
        self.assertEqual(0.0, metrics["average_score"].value)

    def test_no_files_reports_every_assertion_as_failed(self):
        """A prose-only answer must lower the pass-rates, not vanish from them."""
        metrics = self._evaluate(ProposedPipeline(tool_calls=["get_help_or_doc"]))
        for tier in ASSERTION_TIERS:
            with self.subTest(tier=tier):
                self.assertIs(False, metrics[f"{tier}_passed"].value)

    def test_good_pipeline_scores_clean(self):
        metrics = self._evaluate(ProposedPipeline(files={"pipeline.py": GOOD_PIPELINE}))
        self.assertIs(True, metrics["valid_pipeline_passed"].value)
        self.assertEqual(1.0, metrics["average_score"].value)

    def test_invented_connection_is_caught_against_the_profile(self):
        source = GOOD_PIPELINE.replace("dhis2-play", "dhis2-prod-kenya")
        metrics = self._evaluate(ProposedPipeline(files={"pipeline.py": source}))
        self.assertEqual(0.0, metrics["grounding_score"].value)
        self.assertLess(metrics["average_score"].value, 1.0)


class TrajectoryEvaluatorTest(SimpleTestCase):
    def _evaluate(self, calls: list[str]) -> dict:
        ctx = type("Ctx", (), {"output": ProposedPipeline(tool_calls=calls)})()
        return Trajectory().evaluate(ctx)

    def test_records_what_the_agent_did(self):
        metrics = self._evaluate(["list_connections", "create_pipeline"])
        self.assertIs(True, metrics["proposed_a_pipeline"].value)
        self.assertIn("list_connections", metrics["proposed_a_pipeline"].reason)

    def test_prose_only_answer(self):
        metrics = self._evaluate([])
        self.assertIs(False, metrics["proposed_a_pipeline"].value)
        self.assertIn("none", metrics["proposed_a_pipeline"].reason)


class DatasetHashTest(SimpleTestCase):
    def test_hash_is_order_independent(self):
        a, b = make_case("alpha"), make_case("beta")
        self.assertEqual(
            dataset_hash(make_dataset(a, b)), dataset_hash(make_dataset(b, a))
        )

    def test_changing_a_prompt_moves_the_hash(self):
        before = make_dataset(make_case("alpha"))
        after = make_dataset(make_case("alpha"))
        after.cases[0].inputs.prompt = "an edited prompt"
        self.assertNotEqual(dataset_hash(before), dataset_hash(after))

    def test_changing_metadata_moves_the_hash(self):
        before = make_dataset(make_case("alpha", lang="en"))
        after = make_dataset(make_case("alpha", lang="fr"))
        self.assertNotEqual(dataset_hash(before), dataset_hash(after))


class ValidateCasesTest(SimpleTestCase):
    def test_empty_dataset_is_rejected(self):
        with self.assertRaises(DatasetError):
            validate_cases(make_dataset())

    def test_unknown_profile_is_rejected_before_any_model_call(self):
        with self.assertRaises(DatasetError) as ctx:
            validate_cases(make_dataset(make_case("alpha", profile="dhis2_workspce")))
        self.assertIn("dhis2_workspce", str(ctx.exception))

    def test_valid_dataset_passes(self):
        validate_cases(make_dataset(make_case("alpha"), make_case("beta")))


class SuiteRegistryTest(SimpleTestCase):
    def test_unknown_suite_fails_loudly(self):
        with self.assertRaises(KeyError):
            get_suite("pipeline_edit")

    def test_registered_suite_is_complete(self):
        suite = get_suite("pipeline_create")
        self.assertEqual("create-pipeline-outcome-evals", suite.dataset_name)
        self.assertEqual(InstructionSet.CREATE_PIPELINE, suite.instruction_set)
        self.assertTrue(suite.evaluators)

    def test_every_suite_has_a_distinct_dataset(self):
        names = [suite.dataset_name for suite in SUITES.values()]
        self.assertEqual(len(names), len(set(names)))


class InstructionsHashTest(SimpleTestCase):
    def test_hash_is_stable_and_set_specific(self):
        create = instructions_hash(InstructionSet.CREATE_PIPELINE)
        self.assertEqual(create, instructions_hash(InstructionSet.CREATE_PIPELINE))
        self.assertNotEqual(create, instructions_hash(InstructionSet.EDIT_PIPELINE))


class SuiteSelectionTest(SimpleTestCase):
    def test_suite_is_required(self):
        """No default: a forgotten flag must not silently run the wrong suite."""
        with self.assertRaises(CommandError) as ctx:
            call_command("run_evals", "--dry-run")
        self.assertIn("--suite", str(ctx.exception))


class ExperimentNameTest(SimpleTestCase):
    SUITE = get_suite("pipeline_create")
    METADATA = {"model": "opus"}

    def test_defaults_to_suite_and_model(self):
        self.assertEqual(
            "pipeline_create-opus",
            Command._experiment_name(self.SUITE, self.METADATA, None),
        )

    def test_override_wins(self):
        self.assertEqual(
            "baseline-before-prompt-edit",
            Command._experiment_name(
                self.SUITE, self.METADATA, "baseline-before-prompt-edit"
            ),
        )

    def test_empty_override_falls_back_to_the_default(self):
        """An empty --name is a mistake, not a request for an unnamed run."""
        self.assertEqual(
            "pipeline_create-opus",
            Command._experiment_name(self.SUITE, self.METADATA, ""),
        )


class CaseSpreadTest(SimpleTestCase):
    """The per-case summary the built-in report does not print.

    pydantic-evals shows one row per repeat plus a single grand average, so a
    multi-repeat run gives no per-case aggregate. These tests drive a synthetic
    evaluation - a plain function, no model - to check the summary we add.
    """

    HEADLINE = run_evals.HEADLINE_SCORE

    def _report(self, values: dict[str, list[float]], repeat: int):
        seen: dict[str, int] = {}

        class Score(Evaluator):
            def evaluate(self, ctx: EvaluatorContext) -> dict:
                return {
                    CaseSpreadTest.HEADLINE: ctx.output,
                    "valid_sdk_use_passed": ctx.output >= 0.95,
                }

        async def task(inputs: str) -> float:
            index = seen.get(inputs, 0)
            seen[inputs] = index + 1
            return values[inputs][index]

        dataset = Dataset(
            name="spread-test",
            cases=[Case(name=k, inputs=k) for k in values],
            evaluators=[Score()],
        )
        return dataset.evaluate_sync(
            task, repeat=repeat, progress=False, max_concurrency=1
        )

    def _summary(self, values: dict[str, list[float]], repeat: int) -> str:
        command = Command()
        command.stdout = OutputWrapper(StringIO())
        command._print_case_spread(self._report(values, repeat))
        return command.stdout._out.getvalue()

    def test_reports_mean_and_spread_per_case(self):
        out = self._summary({"noisy": [1.0, 0.8, 0.9]}, repeat=3)
        self.assertIn("noisy", out)
        self.assertIn("0.900", out)  # mean
        self.assertIn("0.800", out)  # min
        self.assertIn("0.200", out)  # spread

    def test_a_steady_case_has_zero_spread(self):
        out = self._summary({"steady": [1.0, 1.0, 1.0]}, repeat=3)
        self.assertIn("0.000", out)

    def test_failed_assertions_are_named(self):
        """An assertion that failed in any run is worth seeing per case."""
        out = self._summary({"noisy": [1.0, 0.8, 0.9]}, repeat=3)
        self.assertIn("valid_sdk_use_passed failed", out)

    def test_silent_for_a_single_run(self):
        """With repeat=1 there is nothing to aggregate; the table says it all."""
        self.assertEqual("", self._summary({"solo": [1.0]}, repeat=1))
