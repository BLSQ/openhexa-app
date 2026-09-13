r"""Run an offline agent eval suite as a Django management command.

    docker compose run app manage run_evals --suite={pipeline_create} --repeats=1 \\
        --settings=config.settings.eval

`--settings=config.settings.eval` is required. Unlike the `test` entrypoint,
`manage` does not set a settings module, and the default gives neither the test
isolation nor the Logfire reporting an eval needs: `test.py` disables span
export outright, and `base.py` leaves storage pointing at the real backend. A
run under the wrong settings still costs full price, and fails quietly.

What a run does, in order:

    pull       fetch the suite's cases from Logfire and validate them
    filter     apply --lang and --task-id
    check      confirm Vertex is configured
                 (--dry-run stops here, having spent nothing)
    set up     create the test database and patch the test environment
    evaluate   run each case --repeats times against the real agent
    tear down  drop the database, whatever happened
    report     the per-run table, the per-case spread, the Logfire trace id

The first three steps run against the development database, which is why a dry
run needs no test database. setup_databases() then swaps the connection, and
everything after it sees only the throwaway one.

One suite per invocation. Suites have separate datasets and their scores are not
comparable.
"""

from __future__ import annotations

from statistics import mean

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections

from hexa.assistant.evals.core.dataset import (
    DatasetError,
    experiment_metadata,
    pull_dataset,
    validate_cases,
)
from hexa.assistant.evals.suites import SUITES, get_suite
from hexa.assistant.model_builder import MANAGED_DEFAULT_MODEL
from hexa.core.test.runner import DiscoverRunner
from hexa.user_management.models import AiSettings

# This is the default max concurrency to avoid hitting provider rate limits.
# TODO: Make this a parameter.
MAX_CONCURRENCY = 4

# The score the per-case spread is reported over.
HEADLINE_SCORE = "average_score"


class Command(BaseCommand):
    help = "Run an offline eval suite against the assistant agents."

    def add_arguments(self, parser):
        parser.add_argument(
            "--suite",
            required=True,
            choices=sorted(SUITES),
            help=(
                "Which suite to run. One suite per invocation. Available suites: "
                + ", ".join(sorted(SUITES))
            ),
        )
        parser.add_argument("--repeats", type=int, default=3)
        parser.add_argument(
            "--name",
            dest="experiment_name",
            help=(
                "Name for this experiment in Logfire. Defaults to "
                "<suite>-<model>. Use it to label a run you want to find "
                "again, e.g. 'baseline-before-prompt-edit'."
            ),
        )
        parser.add_argument("--lang", default="all", choices=["all", "en", "fr"])
        parser.add_argument(
            "--task-id",
            action="append",
            dest="task_ids",
            help=(
                "Restrict the run to these task_ids (repeatable). Use with "
                "--repeats=1 for a cheap single-case smoke test."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Pull and validate the dataset, then stop without spending tokens.",
        )

    def handle(self, *args, **options):
        suite = get_suite(options["suite"])
        dataset, metadata = self._prepare(suite, options)
        experiment_name = self._experiment_name(
            suite, metadata, options["experiment_name"]
        )
        self.stdout.write(f"experiment={experiment_name}")

        # Checked before the dry-run exit, so --dry-run covers credentials too.
        self._check_vertex_configured()

        if options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS("Dry run: dataset and credentials are ready.")
            )
            return

        # The project's own DiscoverRunner, not a bare setup_databases(). It
        # creates the `test_<name>` database the guard in evals.fixtures expects,
        # and its setup_test_environment patches get_forgejo_client. Without that
        # patch, creating an Organization calls the real git server.
        #
        # Restricted to the default alias. Otherwise Django also builds a test
        # database for the read-only `dashboard` alias, which has no password
        # outside production.
        runner = DiscoverRunner(verbosity=1, interactive=False)
        runner.setup_test_environment()
        old_config = runner.setup_databases(aliases={DEFAULT_DB_ALIAS})
        try:
            report = dataset.evaluate_sync(
                suite.make_task(),
                name=experiment_name,
                repeat=options["repeats"],
                max_concurrency=MAX_CONCURRENCY,
                metadata=metadata,
            )
        finally:
            self._teardown(runner, old_config)

        report.print(include_input=False, include_output=False)
        self._print_case_spread(report)
        self.stdout.write(
            self.style.SUCCESS(
                f"Experiment reported to Logfire (trace {report.trace_id})."
            )
        )

    @staticmethod
    def _experiment_name(suite, metadata: dict, override: str | None) -> str:
        """What this run is called in Logfire.

        Defaults to <suite>-<model> so unnamed runs stay identifiable. Pass a
        name to mark a run you intend to compare against later.
        """
        return override or f"{suite.name}-{metadata['model']}"

    def _prepare(self, suite, options) -> tuple:
        """Pull, filter and describe the suite, without running anything.

        Separated from handle() so --dry-run exercises the whole pre-flight
        rather than a partial one.
        """
        try:
            dataset = pull_dataset(suite)
            validate_cases(dataset)
        except DatasetError as exc:
            raise CommandError(f"{suite.name}: {exc}") from exc

        lang = options["lang"]
        if lang != "all":
            dataset.cases = [c for c in dataset.cases if c.metadata.lang == lang]
            if not dataset.cases:
                raise CommandError(f"{suite.name}: no cases with lang={lang!r}.")

        task_ids = options["task_ids"]
        if task_ids:
            known = {c.metadata.task_id for c in dataset.cases}
            unknown = sorted(set(task_ids) - known)
            if unknown:
                raise CommandError(
                    f"{suite.name}: unknown task_id(s): {', '.join(unknown)}. "
                    f"Available: {', '.join(sorted(known))}."
                )
            dataset.cases = [c for c in dataset.cases if c.metadata.task_id in task_ids]

        # Evals run on the managed (Vertex) provider only, which always
        # resolves MANAGED_DEFAULT_MODEL regardless of any stored value.
        metadata = experiment_metadata(
            dataset, suite=suite, model=MANAGED_DEFAULT_MODEL
        )
        metadata["lang_filter"] = lang
        metadata["repeats"] = options["repeats"]
        metadata["provider"] = AiSettings.Provider.MANAGED
        # A filtered run is not comparable with a full one. Recorded so a smoke
        # test is never mistaken for an experiment.
        metadata["task_id_filter"] = sorted(task_ids) if task_ids else None

        total = len(dataset.cases) * options["repeats"]
        self.stdout.write(
            f"suite={suite.name} cases={len(dataset.cases)} repeats={options['repeats']} "
            f"runs={total} provider=managed model={metadata['model']}\n"
            f"dataset_hash={metadata['dataset_hash']} "
            f"instructions_hash={metadata['instructions_hash']}"
        )
        return dataset, metadata

    def _print_case_spread(self, report) -> None:
        """Per-case mean and spread across repeats.

        pydantic-evals prints one row per repeat and a single grand average, so
        a three-repeat run is 48 rows with no per-case aggregate. Spread within
        a case is the reason to run repeats at all: a score delta that does not
        clear it is noise.

        Silent for a single-run experiment, where case_groups() returns None.
        """
        groups = report.case_groups()
        if not groups:
            return

        rows = []
        for group in groups:
            scores = [
                run.scores[HEADLINE_SCORE].value
                for run in group.runs
                if HEADLINE_SCORE in run.scores
            ]
            failed = sorted(
                {
                    name
                    for run in group.runs
                    for name, result in run.assertions.items()
                    if not result.value
                }
            )
            rows.append((group.name, scores, len(group.failures), failed))

        width = max(len(name) for name, *_ in rows)
        self.stdout.write(
            f"\nPer-case {HEADLINE_SCORE} over repeats\n"
            f"  {'case'.ljust(width)}  runs   mean    min    max  spread  notes"
        )
        for name, scores, errors, failed in rows:
            notes = []
            if errors:
                notes.append(f"{errors} run(s) errored")
            notes += [f"{name} failed" for name in failed]
            if not scores:
                self.stdout.write(
                    f"  {name.ljust(width)}     -      -      -      -       -  "
                    + "; ".join(notes)
                )
                continue
            spread = max(scores) - min(scores)
            line = (
                f"  {name.ljust(width)}  {len(scores):>4}  "
                f"{mean(scores):>5.3f}  {min(scores):>5.3f}  {max(scores):>5.3f}  "
                f"{spread:>6.3f}  " + "; ".join(notes)
            )
            self.stdout.write(line.rstrip())

    @staticmethod
    def _check_vertex_configured() -> None:
        """Fail before any spend if the managed provider cannot authenticate.

        Vertex uses ambient Google credentials rather than a stored key, so
        there is nothing to resolve, only a project to verify. It is the one
        provider evals support, because it is what production runs on.
        """
        if not settings.VERTEX_PROJECT_ID:
            raise CommandError(
                "VERTEX_PROJECT_ID is not configured, so the managed provider "
                "cannot run. Set VERTEX_PROJECT_ID and VERTEX_REGION, and point "
                "GOOGLE_APPLICATION_CREDENTIALS at credentials with the "
                "roles/aiplatform.user role."
            )

    def _teardown(self, runner, old_config) -> None:
        """Drop the test database, without letting cleanup lose the results.

        The agent runs through sync_to_async, so ORM connections are opened on
        asgiref's executor thread as well as this one. Both must be closed or
        Postgres refuses the DROP. A teardown that still fails is reported and
        swallowed: an orphaned test database is cheap to fix, and raising here
        would discard an experiment that already cost real tokens.
        """
        connections.close_all()
        self._terminate_stray_sessions()
        try:
            runner.teardown_databases(old_config)
        except Exception as exc:  # noqa: BLE001 - never lose the report
            self.stderr.write(
                self.style.WARNING(
                    f"Could not drop the test database ({exc}). "
                    "Drop it by hand if it lingers; results below are unaffected."
                )
            )
        runner.teardown_test_environment()

    @staticmethod
    def _terminate_stray_sessions() -> None:
        """Close any connection still holding the test database open.

        Postgres refuses DROP DATABASE while a session is attached, and the
        agent's async execution can leave one behind on a worker thread. An
        orphaned test database then blocks the next `manage.py test` run with an
        interactive prompt. Best effort: a failure here falls through to the
        warning below.
        """
        name = connections[DEFAULT_DB_ALIAS].settings_dict.get("NAME") or ""
        if not name.startswith("test_"):
            return
        try:
            with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
                cursor.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = %s AND pid <> pg_backend_pid()",
                    [name],
                )
        except Exception:  # noqa: BLE001 - best-effort cleanup
            pass
        connections.close_all()
