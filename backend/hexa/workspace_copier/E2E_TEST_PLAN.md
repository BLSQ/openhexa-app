# Implementation plan: end-to-end tests for `workspace_copier`

## Goal

Replace most of the mock-heavy unit tests in `hexa/workspace_copier/tests/` with
end-to-end tests that run the real copy flow against the real OpenHEXA server
code, in-process, inside the normal Django test suite. A test seeds a genuine
source workspace (ORM), runs `service.run_copy(...)` for real, and asserts on
the resulting target workspace (ORM + `CopyResult`).

Mocks do not disappear entirely: error paths that a healthy in-process server
cannot produce (unreachable hosts, per-file HTTP failures, mid-listing errors)
stay unit-tested. The e2e suite takes over the happy paths and the idempotency
behavior.

### Why this works without a second server

- The copier is effectively **remote→remote over GraphQL**: every implemented
  copier branch talks to both sides through the SDK `Client`. The LOCAL/ORM
  branches are mostly `NotImplementedError` (`resources/workspace.py:130`,
  `resources/pipelines.py`).
- `transport.build_client` already accepts an injectable `http_client`
  (`transport.py:44`) — its docstring explicitly anticipates a WSGI transport
  routed at the in-process app. With
  `httpx.Client(transport=httpx.WSGITransport(app=<django wsgi app>))`, every
  GraphQL request goes through the full real stack: middleware (including
  ServiceAccount Bearer auth, `user_management/middlewares.py:53`), resolvers,
  permission filtering, and the test database — no sockets, no docker.
- Source and target endpoints are opaque to the copier, so pointing both
  clients at the same in-process app faithfully exercises the remote→remote
  flow. (Limitation: both "servers" run the same code version — see Risks.)

---

## Phase 1 — small production refactors (client injection)

Two seams need to become injectable. Both are default-preserving, ~20 lines of
diff total, and improve the design regardless of testing.

### 1a. Thread an HTTP-client factory through `service.py`

`_build_source` / `_build_target` / `_build_existing_target` /
`_build_remote_client` all call `build_client(url, token, label=...)` without
passing `http_client`, so `run_copy` / `run_template_copy` cannot currently be
pointed at an in-process app.

- Add an optional keyword `http_client_factory: Callable[[], httpx.Client] | None = None`
  to `run_copy` and `run_template_copy`.
- Thread it through `_verify_endpoints` → the `_build_*` helpers → each
  `build_client(..., http_client=factory() if factory else None)` call.
  A *factory* (not a shared client) because source and target must each get
  their own client: `build_client` sets the `Authorization` header on the
  client it receives, and the two sides use different tokens.
- Production callers (management command, admin view) pass nothing; behavior
  unchanged.

### 1b. Make `FilesCopier`'s presigned-URL client injectable

`FilesCopier.copy` builds `httpx.Client(timeout=300)` internally
(`resources/files.py:226`) for the presigned download/upload requests. In the
e2e test those URLs are served by the same Django app (see Phase 2, storage),
so this client must also carry the WSGI transport.

- Add a constructor argument, e.g.
  `FilesCopier(skip_existing=False, http_client_factory=None)`, defaulting to
  the current `httpx.Client(timeout=300)`.
- The orchestrator already swaps in a configured `FilesCopier` instance for the
  `skip_existing` flow (`orchestrator.py:63-69`); extend that same mechanism so
  a factory passed to `copy_workspace(...)` (new optional kwarg) reaches the
  files copier. `run_copy` forwards its `http_client_factory` here too.
- Keep the "no auth headers on presigned requests" property (see the comment at
  `resources/files.py:221-225`): the factory used for presigned traffic must
  produce a *bare* client (transport only, no `Authorization` header). In the
  harness this simply means the factory creates a fresh client each call and
  `build_client` only mutates the ones handed to it.

### 1c. Verify (not change): CSRF on `/graphql/` for Bearer requests

Bearer-token requests work against production servers today, so token-auth’d
GraphQL POSTs must already bypass CSRF. Confirm this holds under the test
client during Phase 2 bring-up; if it doesn't, that's a finding about the
middleware ordering, not something to paper over in the harness.

---

## Phase 2 — the e2e harness

New files:

```
hexa/workspace_copier/tests/e2e/
    __init__.py
    harness.py            # base test case + helpers (the only "clever" code)
    test_copy_workspace.py
    test_copy_templates.py   # phase 5
```

### 2a. Base test case (`harness.py`)

A `WorkspaceCopierE2ETestCase(GraphQLTestCase)` (reuse `hexa.core.test`'s base)
whose `setUpTestData`/`setUp` provides:

1. **WSGI-routed SDK clients.**
   `http_client_factory = lambda: httpx.Client(transport=httpx.WSGITransport(app=get_wsgi_application()), base_url="http://testserver")`
   — `ALLOWED_HOSTS = ["*"]` in test settings already permits the host.
   GraphQL URL: `http://testserver/graphql/`.
2. **Service accounts + tokens.** Two `ServiceAccount`s (they are plain `User`
   subclasses; `generate_token()` returns the raw token once):
   - *source SA*: `WorkspaceMembership` (viewer or editor) on the source
     workspace, so it can read workspace/files/pipelines/connections.
   - *target SA*: `OrganizationMembership` with a role allowed to
     `createWorkspace` under the target organization (admin/owner), plus
     workspace membership on the target workspace for re-run scenarios.
   Establish the exact minimum roles empirically during bring-up — that in
   itself documents/verifies the permission contract of the tool.
3. **Real filesystem storage.** The test default is the dummy backend, whose
   presigned URLs point at a fake `http://mockstorage.com` host. Swap in the
   `fs` backend instead — its presigned URLs are Django views
   (`files:upload_file` / `files:download_file`, host taken from
   `settings.BASE_URL`), which the same WSGI transport can serve:
   - `override_settings(BASE_URL="http://testserver")`.
   - `hexa.files.storage` is a module-level `SimpleLazyObject`
     (`hexa/files/__init__.py`), imported by reference everywhere — an
     `override_settings` on `WORKSPACE_STORAGE_BACKEND` does **not**
     re-evaluate it once wrapped. Provide a context-manager/`setUp` helper that
     swaps `storage._wrapped` to a
     `FileSystemStorage(data_dir=<per-test tmpdir>)` and restores the previous
     wrapped value (or resets the lazy object) in `tearDown`. Keep this in one
     place in `harness.py` with a comment explaining the lazy-object caveat.
4. **Patched true externals.** `patch("hexa.workspaces.models.create_database")`
   and `patch("hexa.workspaces.models.load_database_sample_data")` — the same
   pattern every `hexa/workspaces` schema test uses (real Postgres role/DB
   creation needs superuser and leaks state). Nothing else is patched.
5. **A `run(**kwargs)` helper** that calls `service.run_copy` with the WSGI
   client factory, a `NullReporter` (or a `BufferReporter` when a test asserts
   on progress output), and returns the `CopyResult`.

### 2b. Source-workspace factory helpers

Plain ORM builders in `harness.py` (no fixture files — the demo `fixtures`
management command is dev-oriented and drifts):

- `create_source_workspace(...)`: organization + workspace (patched DB
  provisioning), description, countries, docker image.
- `add_files(workspace, {"data/a.csv": b"...", "notebooks/nb.ipynb": b"...", ".ipynb_checkpoints/x": b"..."})`
  — written through the storage backend so listing/download see them; include a
  file inside a `SKIPPED_DIRECTORIES` dir to assert it is *not* copied.
- `add_connection(workspace, ...)` with at least one secret field.
- `add_pipeline(workspace, ...)` with 2+ versions (zipfiles are base64 in the
  DB — trivial to seed), parameters, a schedule, and a `scheduledPipelineVersion`
  pointing at the newest version; add a second pipeline sharing the same *name*
  to cover disambiguation; optionally a notebook-type pipeline whose `.ipynb`
  lives in the seeded files.

---

## Phase 3 — scenario tests (`test_copy_workspace.py`)

Each scenario is one full `run_copy` invocation; assertions go against the ORM
on the target side plus the returned `CopyResult`.

1. **Fresh full copy.**
   - Target workspace created under the target org; name/description/countries
     copied; slug is server-derived (assert prefix + that we *read it back*,
     i.e. `result.workspace_slug == Workspace.objects.get(...).slug`).
   - `docker_image` applied via the follow-up `updateWorkspace`.
   - All non-skipped files present with identical bytes; the
     `.ipynb_checkpoints` file absent; counts in `result.files` match.
   - Connections recreated including secret field values.
   - Pipelines recreated: codes, names, parameters; version count and names;
     schedule + scheduled-version binding points at the right *target* version
     (this pins the "target renumbers versions" server behavior that today is
     only a mocked assumption).
   - Database copier: skipped with a warning (remote→remote), recorded in the
     summary.
   - `format_summary()` renders without error and mentions created resources
     (cheap smoke on the reporting layer).
2. **Idempotent re-run** (`target_workspace_slug=` the slug created in a first
   run): second run creates nothing — files all skipped (key+size match),
   pipelines/connections skipped, workspace metadata untouched (mutate the
   target's description between runs and assert it survives).
3. **Partial re-run repairs the gaps.** After a full copy, delete one pipeline
   and one file on the target, re-run with the slug: exactly those two are
   recreated, everything else skipped.
4. **Resource selection.** `resources={"connections"}`: workspace (mandatory) +
   connections copied; no files, no pipelines; dependency warning recorded when
   selecting `pipelines` without `files`.
5. **Pre-flight failures (still e2e, no mocks).** Invalid token → both-sides
   `CredentialError` messages; nonexistent source slug; nonexistent
   `target_workspace_slug` → aborts before any copying (assert no workspace
   created).
6. **Name-collision disambiguation.** The two same-named source pipelines both
   arrive, with distinct codes/names — now verified against the real
   `createPipeline` resolver instead of a mock that hardcodes the assumption.

Failure-path scenarios that *stay mock-based* (see Phase 4): per-file transfer
failures, mid-listing GraphQL errors, `httpx.ConnectError` mapping, transport
error translation.

## Phase 4 — prune the mock suite

| Existing file | Action |
| --- | --- |
| `tests/resources/test_pipelines.py` | Drop the orchestration tests (creates/skips/disambiguation — covered e2e). Keep `test_failed_pipeline_is_recorded_and_does_not_abort` and `test_notebook_without_path_is_skipped_with_warning` (hard to provoke for real). Rework `UploadVersionsTest` toward pure-function style if feasible. |
| `tests/resources/test_workspace.py` | Drop happy paths; keep the `NotImplementedError` guard for LOCAL until that branch lands. |
| `tests/resources/test_connections.py` | Drop happy paths (covered e2e); keep any per-item failure test. |
| `tests/resources/test_files.py` | Keep failure-path tests (listing failure fallback, per-file failure recording); drop copy/skip happy paths. `is_skipped` tests are pure functions — keep as-is. |
| `tests/resources/test_database.py` | Keep (it's about the skip/warn matrix; cheap). |
| `tests/test_service.py` | Keep `_verify_side` / `CredentialError` unit tests (pure logic). Drop the `RunCopyTest`/`RunTemplateCopyTest` mock plumbing once e2e covers the same flow. |
| `tests/test_orchestrator.py`, `test_transport.py`, `test_command.py`, `test_forms.py` | Keep — small, fast, mostly pure logic or form validation. |

Rule of thumb going forward: a mock is acceptable when it simulates a *failure*
or replaces a *true external*; a mock that returns a happy-path payload the real
server could have produced should be an e2e assertion instead.

## Phase 5 — extensions (separate PRs)

- **Templates copy e2e** (`test_copy_templates.py`): same harness;
  seed a workspace with a template + versions, run `run_template_copy`, assert
  host workspace/pipeline/template/versions on the target and the
  `validatedAt` community-template warning. Re-run for idempotency.
- **Optional `external`-tagged docker smoke**: run the actual
  `copy_workspace` management command between two compose stacks. Nightly /
  manual only — this is the only way to cover cross-version copies, but it must
  not gate the unit suite.

---

## Risks & mitigations

- **Lazy `storage` object swap is fragile** → isolate in one harness helper
  with restore-on-teardown; assert in the helper that the active backend is
  `FileSystemStorage` before any test writes files.
- **Broader failure blast radius** (a pipelines-app regression fails copier
  tests): intended, but keep scenario tests small and named by behavior so the
  failing assertion localizes the problem; `CopyResult` warnings should be
  asserted `== []` in the fresh-copy test so unexpected drift surfaces loudly.
- **Both sides run the same schema version** — cross-version copying stays
  untested in-process; covered only by the optional Phase 5 smoke.
- **SDK (`openhexa.graphql`) vs. schema drift** now breaks these tests. That is
  a real bug for this tool and *should* fail CI; note it in the README.
- **Speed**: one full copy ≈ tens of GraphQL requests through the full stack;
  expected low single-digit seconds per scenario. If `setUpTestData` sharing is
  insufficient, trim seeded content per scenario rather than reintroducing mocks.
- **CSRF / middleware surprises under WSGITransport** (1c): resolve during
  Phase 2 bring-up before writing scenarios.

## Definition of done

- Phases 1–4 merged; `docker compose run app test hexa.workspace_copier --settings=config.settings.test`
  green and not meaningfully slower than ~10–15s for the app.
- Fresh-copy, idempotent re-run, partial re-run, selection, and pre-flight
  scenarios all pass against the real server code with only
  `create_database` / `load_database_sample_data` patched.
- README testing section updated to describe the two-tier strategy (e2e for
  behavior, unit for failure paths / pure logic).

## Suggested PR slicing

1. **PR 1**: Phase 1 refactors + harness + the fresh-copy scenario (proves the
   approach end to end).
2. **PR 2**: remaining scenarios (idempotency, partial, selection, pre-flight,
   disambiguation).
3. **PR 3**: prune mock tests + README update.
4. **PR 4** (optional): templates e2e; docker smoke if wanted.
