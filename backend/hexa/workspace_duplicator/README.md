# workspace_duplicator

Copy an OpenHEXA workspace (and its resources) from one server to another — or between two workspaces on the same server. This is a Django app **with no models**.

## How it works

A single `orchestrator.duplicate_workspace(source, target, *, resources)` owns an ordered registry of **resource copiers** and runs the selected ones in dependency order. Both sides are `Endpoint` values:

- **LOCAL** — same server, read/written via the Django ORM.
- **REMOTE** — another server, reached over GraphQL through `transport.py` after a superuser login.

The read-vs-write asymmetry lives inside each copier (it reads from `source`, writes to `target`), so the orchestration is written once and shared by every entry point. The medium (ORM vs GraphQL) is chosen per endpoint, per resource.

```
service.run_migration(...)        # builds both Endpoints, calls the orchestrator
  └─ orchestrator.duplicate_workspace(source, target, resources)
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

Both are simple wrappers around `service.run_migration`, so we can easily maintain different entry points without causing code drift.

### CLI

TODO: Add more examples.

Example usage:

```
# Localhost to localhost
./manage.py migrate_workspace \
	--source-workspace-slug my-workspace \
	--source-url http://app:8000/graphql/ \
	--source-email root@openhexa.org \
	--source-password root \
	--target-url http://app:8000/graphql/ \
	--target-organization org-uuid \ # optional
	--target-workspace-name "My Workspace (copy)" \ # optional
	--target-email root@openhexa.org \
	--target-password root
```

Note: `--target-workspace-name` is optional and defaults to the same name as the source workspace.

### Django Admin:

On the workspaces list page, there's a new button "Migrate workspace". This provides a view to easily run the CLI script.

The view is Superuser-only and entered credentials are used transiently and never persisted.

## Results

Copiers record what they did/skipped/failed on a shared `DuplicationResult` (per-resource result dataclasses in `results.py`). `format_summary()` renders the human-readable summary shown by both the CLI and the admin page.
