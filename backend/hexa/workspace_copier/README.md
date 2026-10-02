# workspace_copier

Copy an OpenHEXA workspace (and its resources) from one server to another, or between two workspaces on the same server.

From the Django admin, a copy runs as an **async job** on a dedicated worker (see [Async execution](#async-execution)). The CLI still runs it synchronously.

## How it works

A single `orchestrator.copy_workspace(source, target, *, resources)` owns an ordered registry of **resource copiers** and runs the selected ones in dependency order. Both sides are `Endpoint` values:

- **LOCAL**: same server, read/written via the Django ORM.
- **REMOTE**: another server, reached over GraphQL through `transport.py` using a ServiceAccount Bearer token.

The read-vs-write asymmetry lives inside each copier (it reads from `source`, writes to `target`), so the orchestration is written once and shared by every entry point. The medium (ORM vs GraphQL) is chosen per endpoint, per resource.

```
service.run_copy(...)        # builds both Endpoints, calls the orchestrator
  └─ orchestrator.copy_workspace(source, target, resources)
       └─ for each selected ResourceCopier: copy(source, target, result)
```

## Resources (`resources/`)

Each module is the single home for one resource across both mediums. Registry
order (see `orchestrator.WORKSPACE_COPIERS`):

| name          | copier                    | notes                                                                                              |
| ------------- | ------------------------- |----------------------------------------------------------------------------------------------------|
| `workspace`   | `WorkspaceMetadataCopier` | **mandatory** — creates the target, yields its handle                                              |
| `files`       | `FilesCopier`             | bucket objects (streamed through a temp file — see [Large files](#large-files)); the target bucket is listed first and files matching by key + size are skipped, as is anything under a `SKIPPED_DIRECTORIES` scratch dir |
| `database`    | `DatabaseCopier`          | native pg copy only if **both** sides LOCAL; else skipped + warned. Local copy not yet implemented |
| `connections` | `ConnectionsCopier`       | connections + secret fields                                                                        |
| `pipelines`   | `PipelinesCopier`         | pipelines + versions<br>Notes: The `.ipynb` file is copied for notebook pipelines<br>Schedules are not copied to avoid them running immediately after a copy. This allows a human to validate the copied pipeline and schedule it manually.
| `datasets`    | `DatasetsCopier`          | datasets **owned** by the workspace                                                                |

Template pipelines are **not** in this registry — they are server-wide, not a
per-workspace resource, so they are copied by a separate flow (see
[Template pipelines](#template-pipelines) below).

Adding a resource is a drop-in: one module under `resources/` + one registry entry.

### Large files

Each object is streamed through a `tempfile.TemporaryFile` rather than buffered
in memory, so peak RSS is one chunk (`CHUNK_SIZE`) regardless of object size —
buffering whole objects used to get the process OOM-killed on workspaces holding
multi-GB files. Two consequences:

- `TMPDIR` needs room for the largest object being copied. Point it elsewhere
  (`TMPDIR=/mnt/big docker compose run ...`) if the default is small.
- Objects larger than `MAX_UPLOAD_SIZE` (5 GiB, the S3 single-part `PutObject`
  ceiling) are reported as failed without being transferred: a presigned PUT
  cannot do a multipart upload, so they have to be moved by hand.

`TRANSFER_TIMEOUT` bounds a single chunk read/write, not a whole file, so a
stalled connection fails in a couple of minutes while a legitimately slow
multi-GB transfer runs as long as it needs.

## Entry points

Both are simple wrappers around `service.run_copy`, so we can easily maintain different entry points without causing code drift.

### CLI

Example usage:

```
# Localhost to localhost
./manage.py copy_workspace \
	--source-workspace-slug my-workspace \
	--source-url http://app:8000/graphql/ \
	--source-token 'source-service-account-token' \
	--target-url http://app:8000/graphql/ \
	--target-organization org-uuid \
	--target-workspace-name "My Workspace (copy)" \ # optional
	--target-token 'target-service-account-token'

# Production to demo
./manage.py copy_workspace \
	--source-workspace-slug my-workspace \
	--source-url https://api.openhexa.org/graphql/ \
	--source-token 'my-prod-service-account-token' \
	--target-url https://api.demo.openhexa.org/graphql/ \
	--target-organization 002f2f74-7cdb-452c-8ef5-28cc27c04fbe \ # BLSQ org
	--target-workspace-name "My Workspace (copy)" \
	--target-token 'my-demo-service-account-token' \
	--all-dataset-versions # optional; default copies only each dataset's latest version
```

Tokens are ServiceAccount tokens (managed under Django admin → Service accounts). A remote side needs one with permission to read the source workspace / create under the target organization. `--target-workspace-name` is optional and defaults to the same name as the source workspace.

#### Re-running into an existing workspace (idempotency)

By default each run creates a **new** target workspace (the server appends a random suffix to the slug), so if a run is interrupted mid-way, you can't simply repeat.
Pass `--target-workspace-slug` to copy **into an existing workspace** instead:

```
./manage.py copy_workspace \
	--source-workspace-slug my-workspace \
	--source-url https://api.openhexa.org/graphql/ \
	--source-token 'my-prod-service-account-token' \
	--target-url https://api.demo.openhexa.org/graphql/ \
	--target-token 'my-demo-service-account-token' \
	--target-workspace-slug my-workspace-ab12   # slug created by the first run
```

When `--target-workspace-slug` is set:

- the workspace-metadata copier **skips creation** and leaves the existing workspace's metadata untouched;
- every resource copier skips what already exists (pipelines by code, connections by slug, files by key + size), so only the missing pieces are filled in;
- if the slug does **not** exist on the target, the run exists early with a clear message;
- `--target-organization` and `--target-workspace-name` are no longer required or taken into account.

### Django Admin:

On the workspaces list page, there's a button "Copy workspace". Submitting its form **queues** a copy run and redirects to the run's admin page (Workspace copier → Workspace copy runs), which refreshes itself while the run is queued or running and shows its logs and summary.

The view is Superuser-only. Entered credentials are stored encrypted on the run and erased when it ends.

## Async execution

```
admin form ──> WorkspaceCopyRun (QUEUED) + WorkspaceCopyJob  (one transaction)
                       │
workspace_copy_worker ─┴─> queue.execute_copy_run(run_id)
                             └─ service.run_copy(..., reporter=DatabaseReporter(run))
```

- `WorkspaceCopyRun` (`models.py`) holds the inputs, status, timestamps, logs, summary and the target workspace slug. Statuses: `QUEUED` → `RUNNING` → `SUCCESS` / `SUCCESS_WITH_ERRORS` (finished, but some resources failed — see the summary) / `FAILED`.
- The dpq job carries only the run id. Tokens live on the run in `EncryptedTextField`s and are erased when it ends, whatever the outcome.
- The queue is an `AtMostOnceQueue`: the job is committed as claimed before the copy starts, so log lines are visible while it runs. An `AtLeastOnceQueue` would hold one transaction for the whole copy. The trade-off is no automatic retry — see below.
- Run the worker locally with `docker compose --profile workspace_copy_worker up`.

### Interrupted runs and resuming

If the worker stops mid-copy (deploy, out of memory), the run would stay `RUNNING`. On startup, the worker marks every `RUNNING` run as `FAILED` ("interrupted"). **This assumes a single worker replica**: with more, a restarting worker would fail runs another one is still executing.

The target slug is recorded as soon as the target workspace exists, so a failed run's admin page offers **Resume into the same workspace**: it opens the copy form in "existing workspace" mode with the same inputs (tokens must be re-entered). Thanks to [idempotency](#re-running-into-an-existing-workspace-idempotency), only the missing pieces are copied.

## Progress reporting (`progress.py`)

The script never writes to stdout or calls `print` directly. Instead, each entry point supplies a **`ProgressReporter`** that is threaded through `service.run_copy` → `orchestrator.copy_workspace` → every copier. This keeps the orchestration and copiers oblivious to where their output goes.

A reporter exposes `log(message, *, level=...)` plus the `info` / `warning` / `error` shortcuts.

| reporter         | used by                 | behavior                                                                   |
| ---------------- | ----------------------- | -------------------------------------------------------------------------- |
| `NullReporter`   | default / backend tests | discards everything, so the script can run without a caller                |
| `StreamReporter` | CLI                     | writes live to `self.stdout`                                               |
| `BufferReporter` | template copy admin view | collects lines in memory; `render()` produces the text shown after the run |
| `DatabaseReporter` | async workspace copy  | appends lines to `WorkspaceCopyRun.logs` in batches (every ~2s or 50 lines, immediately on warnings/errors) |

## Results

Copiers record what they did/skipped/failed on a shared `CopyResult` (per-resource result dataclasses in `results.py`). `format_summary()` renders the human-readable summary shown by both the CLI and the admin page.

## Template pipelines

Pipeline templates are **server-wide**, not owned by a workspace, so they are copied by their own flow (`templates.copy_templates`) instead of being a resource in the registry above. It runs **once per target server**, independently of any workspace copy, and is **remote→remote only** (both sides need a URL + ServiceAccount token). For each source template it ensures a host pipeline (and its versions) exists on the target, then recreates the template and its versions. It is re-runnable: templates match by name, versions by number.

Note: `validatedAt` is not settable via the API, so an official source template appears as a community template on the target (warned in the summary).

### CLI

```
# --source-url defaults to production (https://api.openhexa.org/graphql/),
# so it can be omitted when copying from prod.
./manage.py copy_templates \
	--source-token 'my-prod-service-account-token' \
	--target-url https://api.demo.openhexa.org/graphql/ \
	--target-token 'my-demo-service-account-token' \
	--target-organization 002f2f74-7cdb-452c-8ef5-28cc27c04fbe # BLSQ org
```

`--target-organization` is where the dedicated "Template pipelines" host workspace is created when it doesn't already exist on the target.

### Django Admin

On the pipeline templates list page, there's a Superuser-only "Copy pipeline templates" button, with the same transient-credentials behavior as the workspace-copy view.
