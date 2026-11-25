# workspace_copier

Copy an OpenHEXA workspace and its resources from one server to another, or between two workspaces on the same server.

There are two ways to run a copy: the Django admin queues it as a background job, the CLI runs it directly.

## What is copied

| Resource    | Notes                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Workspace   | Always copied. An existing target workspace keeps its own metadata.                                                                     |
| Files       | Files already on the target (same path and size) are skipped. Files over 5 GiB are reported as failed and have to be moved by hand.     |
| Database    | Only in a same-server copy. Between servers, see [Copying the database between servers](#copying-the-database-between-servers).         |
| Connections | Secrets included, unless turned off.                                                                                                    |
| Pipelines   | With their versions. Schedules are not copied: check the copied pipeline, then schedule it by hand.                                     |
| Datasets    | Only the datasets owned by the workspace. Only the latest version of each, unless all versions are asked for.                           |
| Web apps    | Static web apps only in a same-server copy. Superset web apps only in a same-server copy within one organization. Iframe web apps always. Subdomains, custom domains and favorites are not copied, so public URLs change. |

A **same-server copy** is a copy between two workspaces of the server the copy runs on: `--same-server` on the CLI, "This server" as both source and target in the admin.

Whatever is skipped or fails is listed in the summary at the end of the run.

## Tokens

Each side needs a ServiceAccount token (Django admin → Service accounts), this server included. The source token must be able to read the source workspace; the target token must be able to create a workspace in the target organization, or edit the existing target workspace.

## CLI: `copy_workspace`

```
# Within this server (no URLs), database and static web apps included
./manage.py copy_workspace --same-server \
	--source-workspace-slug my-workspace \
	--source-token 'source-service-account-token' \
	--target-organization org-uuid \
	--target-workspace-name "My Workspace (copy)" \ # optional, defaults to the source name
	--target-token 'target-service-account-token'

# Production to demo
./manage.py copy_workspace \
	--source-workspace-slug my-workspace \
	--source-url https://api.openhexa.org/graphql/ \
	--source-token 'my-prod-service-account-token' \
	--target-url https://api.demo.openhexa.org/graphql/ \
	--target-organization 002f2f74-7cdb-452c-8ef5-28cc27c04fbe \ # BLSQ org
	--target-token 'my-demo-service-account-token' \
	--all-dataset-versions # optional
```

`./manage.py copy_workspace --help` lists every option. Two are worth knowing:

- `--resources` limits the copy to some resources, e.g. `--resources database`.
- `--disable-ssl-verification` turns off TLS certificate verification for the whole run. Use it only for a server whose certificate is known to be expired or self-signed: tokens and data are then exposed to anyone able to intercept the connection.

### Re-running into an existing workspace

Each run creates a new target workspace by default. To finish an interrupted run, or to add resources later, pass the slug of the workspace to copy into. Everything that already exists there is skipped, so only the missing pieces are copied.

```
./manage.py copy_workspace \
	--source-workspace-slug my-workspace \
	--source-url https://api.openhexa.org/graphql/ \
	--source-token 'my-prod-service-account-token' \
	--target-url https://api.demo.openhexa.org/graphql/ \
	--target-token 'my-demo-service-account-token' \
	--target-workspace-slug my-workspace-ab12 # slug created by the first run
```

`--target-organization` and `--target-workspace-name` are not needed then.

## CLI: `copy_templates`

Pipeline templates belong to a server, not to a workspace, so they have their own command. It copies every template from one server to another and can be re-run: existing templates and versions are skipped.

```
# --source-url defaults to production
./manage.py copy_templates \
	--source-token 'my-prod-service-account-token' \
	--target-url https://api.demo.openhexa.org/graphql/ \
	--target-token 'my-demo-service-account-token' \
	--target-organization 002f2f74-7cdb-452c-8ef5-28cc27c04fbe # BLSQ org
```

`--target-organization` is where the "Template pipelines" workspace holding the copied templates is created when it doesn't exist yet. Official templates arrive as community templates: validate them again on the target.

## Django admin

Both views are for superusers only.

- **Copy workspace**: button on the workspaces list page. Submitting the form queues a run and opens its page (Workspace copier → Workspace copy runs), which shows the logs and summary as the run progresses.
- **Copy pipeline templates**: button on the pipeline templates list page.

A failed or interrupted run is not retried. To finish it, start a new copy into the workspace it created (the run's "Result workspace slug") with "Copy into an existing workspace".

## Copying the database between servers

Not automated: copy it by hand with both workspaces' database credentials, from a machine that can reach both database hosts and has a `pg_dump` at least as recent as the source server.

1. In each workspace, open **Database** and copy the connection URL.
2. Make sure the target database is empty, then run:

   ```
   pg_dump -Fc --no-owner --no-acl "$SOURCE_URL" \
     | pg_restore --no-owner --no-acl -d "$TARGET_URL"
   ```

`pg_restore` may report errors on the `postgis` / `postgis_topology` extensions (e.g. `must be owner of extension`). They are harmless; check that any other error is not a real one. With PostgreSQL 17+ clients, add `--exclude-extension='postgis*'` to `pg_dump` to avoid them.

## Setup and troubleshooting

- **Worker**: copies queued from the admin are run by a dedicated worker. Locally: `docker compose --profile workspace_copy_worker up`.
- **Database copy refused because of open connections**: Postgres cannot copy a database someone is connected to. Close the connections (notebooks, pipelines, BI tools) and re-run into the same target workspace.
- **Database step skipped**: a target database that already holds data is never overwritten.
- **Static web apps fail with a message about `ALLOWED_DOMAINS`**: Forgejo refuses to clone from private addresses, itself included. Add the host of `GIT_SERVER_URL` to its allow-list:

  ```
  [migrations]
  ALLOWED_DOMAINS = <host of GIT_SERVER_URL>   # env: FORGEJO__migrations__ALLOWED_DOMAINS
  ```

- **Not enough disk space for large files**: each file passes through the temporary directory, which needs room for the largest one. Point `TMPDIR` to a bigger disk.

## Design decisions

The code is the reference for how the copier works. These are the choices that are easy to undo by accident:

- **Every server is reached over GraphQL, this one included.** The copy is written once and behaves the same from the CLI and the admin, which are both thin wrappers around `service.run_copy`.
- **A same-server copy is declared, never guessed.** A URL has several valid spellings for the same server, so comparing URLs would be unreliable. The run checks up front that both workspaces really are on this server.
- **The database and static web apps are same-server only** because they need direct access to the server's database and git server, which GraphQL does not give.
- **The database copy is built under a staging name and swapped in on success**, so a failed copy leaves the target untouched.
- **Files are streamed through a temporary file** instead of memory: buffering multi-GB files got the process killed.
- **The job queue is at-most-once.** The job is committed as claimed before the copy starts, which is what makes the logs visible while it runs; an at-least-once queue would hold one transaction for the whole copy. The price is no automatic retry.
- **Only one worker copies at a time**, enforced by a Postgres advisory lock. On startup a worker marks unfinished runs as failed, which is only correct once no other worker is still copying; in a rolling deploy the new worker waits for the old one to exit.
- **Tokens are stored encrypted on the run and erased when it ends**, whatever the outcome.
