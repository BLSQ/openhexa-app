# data_studio — SQL editor

This app owns the Data Studio product surface: saved queries (`models.SavedQuery`), the
query audit log (`models.QueryLog`), and the two ways a user runs SQL — the interactive
`Database.executeSQL` GraphQL field (`schema`, over `query_runner`) and the full-result
CSV download (`views.download_query_csv`).

Talking to a workspace database is *not* this app's job. Connections, introspection and
the execution primitives (`execute_database_query`, `stream_database_query`) live in
`hexa.databases`, which knows nothing about this app: the dependency runs one way,
`data_studio` → `databases`. What lands on which side follows from where `QueryLog` lives
— anything that has to write an audit entry belongs here, so `query_runner` (permission
check → execute → log) sits here while the psycopg2 plumbing it calls stays there. Two
consequences worth knowing:

- `executeSQL` is declared as `extend type Database` in this app's schema, even though
  `Database` itself is defined by `hexa.databases`.
- The permission both paths enforce is `databases.run_query` — whether a user may run SQL
  against a workspace database is a property of the database, not of the Data Studio.

Both paths go through `query_runner`, which is the only module that writes `QueryLog`:
`run_and_log_database_query` for the interactive path, `stream_and_log_database_query` for
the export, and `ensure_can_run_query` for the permission check they share (the export
calls it separately so it can refuse a request before reserving a concurrency slot).

The rest of this file is the design-decision home for the CSV export; the code carries
short "why" comments that point here.

## Saved query history

A saved query's SQL is versioned in a git repository of its own holding a single
`query.sql`, the mechanism `hexa/git` describes. Only the SQL: renaming a query or
resharing it records nothing.

`content` stays the source of truth — running, exporting, listing a query and serving it to
a web app all read that column, never the git server. A version is committed inside the
same transaction as the row, so a git failure fails the save (`VERSIONING_UNAVAILABLE`)
rather than keeping a change with no history. Deleting is the exception: archiving happens
after the commit and cannot fail the deletion.

There is no published version; the current one runs. `last_commit` says which commit
`content` matches, so drift can be found (`manage.py backfill_saved_query_repositories
--check`), and it is also what says the repository exists — migration 0010 named one for
every existing query without creating any. That command creates them; anything it misses
heals on the query's next save through `ensure_repo`.

## Why the export streams (rather than buffers)

The full result is streamed batch by batch (`hexa.core.csv.async_streaming_csv_response`)
off a server-side named cursor, with **no row cap**, so bytes reach the browser as the
query produces them (no full-serialisation delay, no proxy idle-timeout) and peak memory
stays bounded to one `DOWNLOAD_QUERY_BATCH_SIZE` batch whatever the result size.

It is an **async** stream on purpose: under the ASGI worker a sync stream is silently
drained into memory in one go (`StreamingHttpResponse.__aiter__` falls back to
`sync_to_async(list)`), defeating the point — so the blocking psycopg2 fetches are pushed
off the event loop via `sync_to_async(thread_sensitive=False)`.

The query runs and its first batch is fetched **eagerly** (`stream_database_query`), so
the common failures — invalid SQL, permission error, empty statement — surface as a clean
HTTP 400 *before* any byte is sent.

## The streaming trade-off: silent truncation

Once the headers are sent the status is fixed at 200, so a failure *after* the first batch
(a mid-scan timeout, a dropped connection) can't become an error status — the download ends
truncated, opening cleanly but short its trailing rows. These are logged as a WARNING (row
count, workspace, user) in `_tracked_row_batches`.

It is unlikely by design: the eager first fetch turns front-loaded queries (sorts, hash
aggregates, large joins) into a clean 400, and `statement_timeout` bounds each `FETCH`, not
the whole scan, so a legitimately long export never trips it. The realistic causes are infra
events — the workspace DB connection dropping, or the worker killed mid-stream (deploy, OOM) —
which surface through other signals too. The stream is uncompressed (`SSEAwareGZipMiddleware`
skips async streams: Django 5.2 gzips them one member per chunk, undecodable by browsers;
revisit on Django 6.0), so there is no gzip layer or Content-Length to flag a short body
either. If it ever matters, the fix is to buffer the CSV to a temp spool first (real
Content-Length and error status, at the cost of latency and disk) — deliberately not done.

## Auditing the export

Every export writes a `QueryLog` entry — these are the runs with no row cap, so they are the
ones worth having on record. Two things work differently from the interactive path.

**The entry is written twice.** A streamed export only knows its outcome (row count, duration,
mid-stream failure) long after the response was accepted, and writing the entry that late
would lose the trail exactly when it matters most: a worker killed mid-download. So
`stream_and_log_database_query` writes it as soon as the query has run, at status `STREAMING`,
and `QueryExportAudit` updates it to `SUCCESS`/`ERROR` when the stream ends. An entry left at
`STREAMING` therefore means the end was never observed — a cancelled download, a dropped
connection, a dead worker. A failed *first* write fails the request closed (as the interactive
path does); a failed *final* update is only logged, since the bytes are already on the wire and
the run is already on record.

**The origin is server-set.** `DATA_STUDIO_EXPORT` is applied by the view rather than taken
from a client-supplied argument, and is deliberately absent from the `ExecuteSQLOrigin` GraphQL
enum (`schema` binds only the client-settable subset), so the value always means a real uncapped
export. Beware that `duration_ms` here covers the whole export — which the client paces by
consuming the stream — so it is not comparable to the interactive path's database time.

Requests refused before any SQL reaches the database are logged too: `DENIED` (no permission)
and `REJECTED` (multiple statements, or no free export slot — so a pool running out is visible
in the log). Requests with nothing to audit are not: an unknown workspace, an empty statement.

The frontend's other download path builds its CSV from rows an `executeSQL` already returned,
so it re-runs nothing and stays audited as that `DATA_STUDIO` query; only the uncapped re-run
appears as `DATA_STUDIO_EXPORT`.

## Bounding runaway work

A read-only DB connection is held open for the whole download. Three bounds keep that from
becoming a liability. The first two are set by `hexa.databases.utils.stream_database_query`,
the third by `views`:

- **`statement_timeout`** bounds a runaway per-batch scan.
- **`idle_in_transaction_session_timeout`** bounds a stalled client, so a vanished browser
  can't pin the transaction (and block VACUUM) forever.
- **`_EXPORT_SLOTS`** (a `BoundedSemaphore`, size `DATA_STUDIO_EXPORT_MAX_CONCURRENCY`) bounds
  concurrent exports per worker; excess callers get an immediate **429** rather than queueing.
  It is per process, not a global cap (that is the per-role Postgres `CONNECTION LIMIT`).

## Resource lifecycle

The slot and connection outlive the view call — the response keeps consuming rows after the
view returns — so they are freed when the *stream* ends, via `async_streaming_csv_response`'s
`on_finish` (fires exactly once on completion, mid-stream error, and client disconnect alike).
The disconnect case is subtle: an async generator's `finally` runs only at GC time, so cleanup
hangs off Django's deterministic `response.close()` (`_CleanupStreamingHttpResponse`), with a
once-guard making the two routes to cleanup safe.

## The "download began" signal (cookie handshake)

A successful attachment goes straight to the browser's download manager without navigating the
hidden iframe the frontend posts into, so the page gets no `load` event to confirm the download
started. The backend signals it with a short-lived, JS-readable cookie whose **name** carries
the caller's token (`csvDownloadToken-<token>`), which the frontend polls for; a per-token name
keeps concurrent downloads from clobbering each other. It signals "began", not "completed" — a
mid-stream failure can't retract it.

These cross-tier constants (cookie prefix, POST field names) must agree with no shared code
path, so they live in a contract fixture (`tests/fixtures/download_contract.json`) asserted on
both sides — see `tests/test_views.py` and `DataStudioEditor/downloadQueryCsv.test.ts`.

## Known limitation

Duplicate column names in a result (`SELECT a.id, b.id …`) collapse under `RealDictCursor`, so
the CSV repeats one value. Pre-existing and not export-specific — the interactive path is
affected identically.
