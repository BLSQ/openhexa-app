# workspace_copier

Copy an OpenHEXA workspace (and its resources) from one server to another, or between two workspaces on the same server.

Right now, this is a Django app **without models**. In the future, some models will be introduced to support moving the execution of this script to an async job.

## How it works

A single `orchestrator.copy_workspace(source, target, *, resources)` owns an ordered registry of **resource copiers** and runs the selected ones in dependency order. Both sides are `Endpoint` values:

- **LOCAL**: same server, read/written via the Django ORM.
- **REMOTE**: another server, reached over GraphQL through `transport.py` after a superuser login.

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
| ------------- | ------------------------- | -------------------------------------------------------------------------------------------------- |
| `workspace`   | `WorkspaceMetadataCopier` | **mandatory** — creates the target, yields its handle                                              |
| `files`       | `FilesCopier`             | bucket objects                                                                                     |
| `database`    | `DatabaseCopier`          | native pg copy only if **both** sides LOCAL; else skipped + warned. Local copy not yet implemented |
| `connections` | `ConnectionsCopier`       | connections + secret fields                                                                        |
| `pipelines`   | `PipelinesCopier`         | pipelines + versions (depends on `files` for notebook pipelines)                                   |

`templates.py` (`TemplatesCopier`) is **not** in the registry — template pipelines are server-wide and copied by a separate flow.

Adding a resource is a drop-in: one module under `resources/` + one registry entry.

## Entry points

Both are simple wrappers around `service.run_copy`, so we can easily maintain different entry points without causing code drift.

### CLI

Example usage:

```
# Localhost to localhost
./manage.py copy_workspace \
	--source-workspace-slug my-workspace \
	--source-url http://app:8000/graphql/ \
	--source-email root@openhexa.org \
	--source-password root \
	--target-url http://app:8000/graphql/ \
	--target-organization org-uuid \ # optional
	--target-workspace-name "My Workspace (copy)" \ # optional
	--target-email root@openhexa.org \
	--target-password root

# Production to demo
./manage.py copy_workspace \
	--source-workspace-slug my-workspace \
	--source-url https://api.openhexa.org/graphql/ \
	--source-email me@bluesquarehub.com \
	--source-password 'my-prod-pw' \
	--target-url https://api.demo.openhexa.org/graphql/ \
	--target-organization 002f2f74-7cdb-452c-8ef5-28cc27c04fbe \ # BLSQ org
	--target-workspace-name "My Workspace (copy)" \
	--target-email me@bluesquarehub.com \
	--target-password 'my-demo-pw''
```

Note: `--target-workspace-name` is optional and defaults to the same name as the source workspace.

### Django Admin:

On the workspaces list page, there's a new button "Copy workspace". This provides a view to easily run the CLI script.

The view is Superuser-only and entered credentials are used transiently and never persisted.

## Progress reporting (`progress.py`)

The script never writes to stdout or calls `print` directly. Instead, each entry point supplies a **`ProgressReporter`** that is threaded through `service.run_copy` → `orchestrator.copy_workspace` → every copier. This keeps the orchestration and copiers oblivious to where their output goes.

A reporter exposes `log(message, *, level=...)` plus the `info` / `warning` / `error` shortcuts.

| reporter         | used by                 | behavior                                                                   |
| ---------------- | ----------------------- | -------------------------------------------------------------------------- |
| `NullReporter`   | default / backend tests | discards everything, so the script can run without a caller                |
| `StreamReporter` | CLI                     | writes live to `self.stdout`                                               |
| `BufferReporter` | Django admin view       | collects lines in memory; `render()` produces the text shown after the run |

Note: `BufferReporter` is also the shape a future async-job reporter could follow, by appending lines to a "logs" field on a run record (see the docstring).

## Results

Copiers record what they did/skipped/failed on a shared `CopyResult` (per-resource result dataclasses in `results.py`). `format_summary()` renders the human-readable summary shown by both the CLI and the admin page.
