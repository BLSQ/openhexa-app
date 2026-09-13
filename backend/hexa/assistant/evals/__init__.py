"""Offline evaluation harness for the OpenHEXA assistant agents.

A run pulls cases from a hosted Logfire dataset, replays each one against the
real agent in a throwaway workspace, scores what the agent produced, and reports
an experiment back to Logfire. `manage.py run_evals` is the entry point.

    core/        machinery that does not know which agent is under test
    fixtures.py  the seeded workspaces cases run against, shared by all suites
    suites/      one package per agent under test
    verifiers/   the scoring rules, grouped by the kind of artifact they read

A suite is the unit of extension. Adding an agent means adding a suite package,
and a verifier package beside `verifiers/pipelines` if it produces a new kind of
artifact.

Nothing here is collected by `manage.py test`, which only looks for `test*.py`.
Eval runs cost real model tokens, so they have to be started deliberately. The
verifier unit tests live in `hexa/assistant/tests/` and run with `make t`.
"""
