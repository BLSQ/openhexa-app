# data_studio — SQL editor

This app owns the Data Studio product surface: saved queries (`models.SavedQuery`),
the query audit log (`models.QueryLog`) and the CSV export endpoint
(`views.download_query_csv`).

Talking to a workspace database is *not* this app's job — connections, introspection
and the query primitives (`execute_database_query`, `stream_database_query`) live in
`hexa.databases`, and the interactive editor path runs through its `Database.executeSQL`
GraphQL field. The dependency runs one way: `data_studio` → `databases`. The permission
gating both paths is `databases.run_query`, for the same reason.

The rest of this file is the design-decision home for the CSV export; the code carries
short "why" comments that point here.

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
