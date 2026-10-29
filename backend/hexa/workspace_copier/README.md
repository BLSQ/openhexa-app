# workspace_copier

Copy an OpenHEXA workspace (and its resources) from one server to another, or between two workspaces on the same server.

From the Django admin, a copy runs as an **async job** on a dedicated worker (see [Async execution](#async-execution)). The CLI still runs it synchronously.

## How it works

A single `orchestrator.copy_workspace(source, target, *, resources)` owns an ordered registry of **resource copiers** and runs the selected ones in dependency order. Both sides are `Endpoint` values, reached over GraphQL through `transport.py` using a ServiceAccount Bearer token — this server included (a blank server URL means this server's own GraphQL endpoint, `INTERNAL_BASE_URL/graphql/`).

The read-vs-write asymmetry lives inside each copier (it reads from `source`, writes to `target`), so the orchestration is written once and shared by every entry point.

Two resources need direct access to the server's database and git server, so they only run in a **same-server copy** (`--same-server` on the CLI, "Both workspaces are on this server" in the admin): the workspace [database](#database) and [static web apps](#static-web-apps-on-the-same-server). The operator states it explicitly rather than the copier guessing from URLs, which have several valid spellings for the same server. Pre-flight checks that the source workspace (and an existing target) are in this server's database, so a wrong flag stops the run before anything is copied.

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
| `database`    | `DatabaseCopier`          | native Postgres copy in a same-server copy; else skipped with manual instructions — see [Database](#database) |
| `connections` | `ConnectionsCopier`       | connections + secret fields                                                                        |
| `pipelines`   | `PipelinesCopier`         | pipelines + versions<br>Notes: The `.ipynb` file is copied for notebook pipelines<br>Schedules are not copied to avoid them running immediately after a copy. This allows a human to validate the copied pipeline and schedule it manually.
| `datasets`    | `DatasetsCopier`          | datasets **owned** by the workspace                                                                |
| `webapps`     | `WebappsCopier`           | web apps<br>Notes: Static web apps are copied **only in a same-server copy** — see [Static web apps on the same server](#static-web-apps-on-the-same-server): Forgejo clones the repository into the target organization itself (`POST /repos/migrate`), so every commit, branch, author and date is kept, there is no file size limit, and the commit shas are unchanged — the published version carries over as-is. The row is written with the ORM; the copy keeps the source repository's visibility, and branch protection and the git proxy collaborator are applied again. If the clone fails Forgejo removes it; if the row then cannot be saved the repository is deleted, so a re-run retries it.<br>Across servers, static web apps are skipped with a warning.<br>Iframe web apps are recreated from their URL. Superset web apps are skipped with a warning.<br>Subdomains, custom domains, favorites and the "powered by" setting are not copied, so public web app URLs change. |

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

## Database

In a same-server copy, the target database is replaced by a native copy of the source (`CREATE DATABASE ... WITH TEMPLATE`, see `hexa.databases.api.replace_empty_database_with_copy`). This is a file-level copy, much faster than a dump/restore.

A run without `--same-server` skips the database and prints the command to copy it afterwards into the workspace it created:

```
./manage.py copy_workspace --same-server \
	--source-workspace-slug my-workspace \
	--target-workspace-slug my-workspace-ab12 \
	--resources database \
	--source-token 'service-account-token' \
	--target-token 'service-account-token'
```

- **No open connections**: Postgres refuses to copy a database while anyone is connected to it. The copier checks first and fails early with the number of open connections (notebooks, pipelines, BI tools...). Close them and re-run into the same target workspace with `--target-workspace-slug`. During the copy itself, new connections to the source are refused.
- **The target database is never overwritten** once it holds data (any table or view besides PostGIS's own): the database step is skipped instead.
- The target workspace keeps its own roles and credentials. The copy is built under a staging name (`<db_name>_copy`) and only swapped in once it succeeded, so a failed copy leaves the target database untouched.

### Copying between servers

Not automated yet: the copy summary prints these steps. Copy the database manually with both workspaces' database credentials, from a machine that can reach both database hosts and has a `pg_dump` at least as recent as the source server:

1. In each workspace, open **Database** and copy the connection URL (or read `workspace { database { credentials { url } } }` over GraphQL).
2. Make sure the target database is empty, then run:

   ```
   pg_dump -Fc --no-owner --no-acl "$SOURCE_URL" \
     | pg_restore --no-owner --no-acl -d "$TARGET_URL"
   ```

   PostGIS already exists in every workspace database and belongs to the server admin, so `pg_restore` may report errors on the `postgis` / `postgis_topology` extensions (e.g. `must be owner of extension`). They are harmless and the rest of the restore goes on; check that any other error is not a real one. With PostgreSQL 17+ clients, add `--exclude-extension='postgis*'` to `pg_dump` to avoid them.

Tables are restored as owned by the target workspace role, so the workspace's read-only role can read them automatically.

## Entry points

Both are simple wrappers around `service.run_copy`, so we can easily maintain different entry points without causing code drift.

### CLI

Example usage:

```
# Within this server (blank URLs), database and static web apps included
./manage.py copy_workspace --same-server \
	--source-workspace-slug my-workspace \
	--source-token 'source-service-account-token' \
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

Tokens are ServiceAccount tokens (managed under Django admin → Service accounts). Each side, this server included, needs one with permission to read the source workspace / create under the target organization. `--target-workspace-name` is optional and defaults to the same name as the source workspace.

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
- every resource copier skips what already exists (pipelines by code, connections by slug, files by key + size, web apps by name), so only the missing pieces are filled in;
- if the slug does **not** exist on the target, the run exists early with a clear message;
- `--target-organization` and `--target-workspace-name` are no longer required or taken into account.

#### Static web apps on the same server

Static web apps are copied in a same-server copy (`--same-server`, or "Both workspaces are on this server" in the admin). The run copies everything else as usual over GraphQL, and static web apps in the same run, directly through the ORM and Forgejo, since both workspaces are in this server's database. Iframe web apps still go through GraphQL.

Without the option, static web apps are skipped with a warning. With it, if a workspace turns out not to be on this server (a new target created on another one), each static web app fails with a message saying so.

Forgejo refuses to clone from private network addresses by default, itself included. The server's Forgejo needs the host of `GIT_SERVER_URL` in its allow-list (`forgejo` in `docker-compose.yaml`):

```
[migrations]
ALLOWED_DOMAINS = <host of GIT_SERVER_URL>   # env: FORGEJO__migrations__ALLOWED_DOMAINS
```

Without it, each static web app fails with a message naming this setting, and the run ends as `SUCCESS_WITH_ERRORS`. The copy worker must also be able to reach Forgejo (`GIT_SERVER_URL` and the admin credentials).

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
- The queue is an `AtMostOnceQueue`: the job is committed as claimed before the copy starts, so log lines are visible while it runs. An `AtLeastOnceQueue` would hold one transaction for the whole copy. The trade-off is no automatic retry — see [Interrupted runs](#interrupted-runs).
- Run the worker locally with `docker compose --profile workspace_copy_worker up`.

### Interrupted runs

If the worker stops mid-copy (deploy, out of memory), the run would stay `RUNNING`. And because the queue deletes a job as soon as the worker claims it, a crash right after claiming would leave the run `QUEUED` with no job left to pick it up. On startup, the worker marks both as `FAILED` ("interrupted") and erases their tokens.

That cleanup is only correct if no other worker is still copying, so the worker first takes a Postgres advisory lock (`pg_advisory_lock`). In a rolling deploy, the new worker waits until the old one has exited before cleaning up. Only one worker runs at a time; extra replicas just wait. The lock is tied to the worker's database session, so Postgres releases it however the process ends (crash included).

A failed run is not retried. To finish it, start a new copy from the admin into the workspace it created (its "Result workspace slug", recorded even when the run fails) in "existing workspace" mode; thanks to [idempotency](#re-running-into-an-existing-workspace-idempotency), only the missing pieces are copied.

## Progress reporting (`progress.py`)

The script never writes to stdout or calls `print` directly. Instead, each entry point supplies a **`ProgressReporter`** that is threaded through `service.run_copy` → `orchestrator.copy_workspace` → every copier. This keeps the orchestration and copiers oblivious to where their output goes.

A reporter exposes `log(message, *, level=...)` plus the `info` / `warning` / `error` shortcuts.

| reporter         | used by                 | behavior                                                                   |
| ---------------- | ----------------------- | -------------------------------------------------------------------------- |
| `NullReporter`   | default / backend tests | discards everything, so the script can run without a caller                |
| `StreamReporter` | CLI                     | writes live to `self.stdout`                                               |
| `BufferReporter` | template copy admin view | collects lines in memory; `render()` produces the text shown after the run |
| `DatabaseReporter` | async workspace copy  | appends lines to `WorkspaceCopyRun.logs` in batches (every 50 lines, on the first line logged 2s after the last write, and immediately on warnings/errors) |

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
