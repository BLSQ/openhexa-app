# databases — Data Studio query & CSV export

This app backs the Data Studio SQL editor: running a read-only query against a
workspace database (`utils.execute_database_query`, exposed over GraphQL) and
exporting a query's **full** result set as a CSV download (`views.download_query_csv`).

This document is the design-decision home for the export. The code carries only
short "why" comments and points here for the longer rationale, so that analysis
lives in one place instead of rotting inside a function docstring.

## Two export paths

The same query can be exported two ways; the frontend picks based on whether the
interactive result was truncated (see `DataStudioEditor/useDataStudioQuery.ts`):

- **Fast (client-side).** The interactive run already returned the whole result
  (not truncated), so every row is in the browser. The CSV is built client-side
  (`DataStudioEditor/csv.ts`) — instant, no second DB round-trip, exports the
  exact on-screen snapshot, and cannot fail. Bounded by the interactive row cap.
- **Heavy (server streaming).** The interactive result was capped, so the full
  set is larger than the browser holds. The frontend re-runs the query
  server-side (`views.download_query_csv`) with **no row cap** and streams the
  entire result to disk.

The two paths must emit **byte-identical** CSV for the same data. That contract is
pinned by a shared fixture (`hexa/core/tests/fixtures/csv_cell_vectors.json`)
asserted on both tiers — see `hexa.core.csv` and `DataStudioEditor/csv.parity.test.ts`.

## Why the heavy path streams (rather than buffers)

The result is streamed batch by batch (`hexa.core.csv.async_streaming_csv_response`)
off a server-side named cursor, so:

- bytes reach the browser as soon as the query produces them — a large export is
  neither delayed by full serialisation nor exposed to a proxy idle-timeout while
  nothing is sent;
- peak memory stays bounded to one `DOWNLOAD_QUERY_BATCH_SIZE` batch regardless of
  result size.

It is an **async** stream on purpose: under the ASGI worker a sync stream would be
silently drained into memory in one go (`StreamingHttpResponse.__aiter__` falls
back to `sync_to_async(list)`), defeating the point. The blocking psycopg2 fetches
are therefore pushed off the event loop via `sync_to_async(thread_sensitive=False)`.

The query is executed and its first batch fetched **eagerly** (`stream_database_query`),
so the common failures — invalid SQL, permission error, empty statement — surface
as a clean HTTP 400 *before* any byte is sent.

## The streaming trade-off: silent truncation

Once the response has sent its headers the status is fixed at 200. A failure
*after* the first batch (a statement timeout mid-scan, a dropped connection) can no
longer become an error status — the download just ends truncated, opening cleanly
but missing its trailing rows, with no client-side error. Such failures are logged
as a WARNING (row count, workspace, user) in `_tracked_row_batches`, so a short file
stays observable server-side.

**How likely is this?** Low, by design, and the residual causes are infrastructural
rather than query-shaped:

- **Front-loaded query cost is caught, not truncated.** The eager first fetch means
  any query whose cost is paid up front — a sort, a hash aggregate, a large join that
  must materialise before the first row — fails during that fetch and becomes a clean
  400. Only a query that is *cheap to start and expensive to sustain* (a plain
  streaming scan) can get past the first byte and then fail.
- **`statement_timeout` bounds a single batch, not the whole scan.** With the
  server-side named cursor each `FETCH` is its own statement, so `DOWNLOAD_QUERY_TIMEOUT_MS`
  limits one batch — not the total download. A legitimately long export (many minutes
  of steady streaming) never trips it as long as each batch returns within the limit.
- **`idle_in_transaction_session_timeout` fires only on a stalled client.**
  `DOWNLOAD_QUERY_IDLE_TIMEOUT_MS` aborts the transaction only if the client stops
  consuming mid-stream — by which point the user's own download has visibly stalled
  anyway, so a truncated file is not a silent surprise.

That leaves genuine infra events as the realistic causes: the workspace DB connection
dropping (restart, failover, network blip) or the web worker being killed mid-stream
(deploy, OOM, or a scale-down outlasting gunicorn's graceful-shutdown window). These
are infrequent and usually visible through other signals (deploy notices, error
rates), not only through a short CSV.

### Why not gzip, and why no Content-Length

The stream is served **uncompressed**: `SSEAwareGZipMiddleware` skips async streams
because Django 5.2 gzips them one member per chunk, which browsers can't reliably
stream-decode (revisit once on Django 6.0). So there is no gzip layer to also flag a
truncated body, and no Content-Length either.

### The fallback we deliberately don't use

If silent truncation ever proves to matter in practice, the fix is to buffer the whole
CSV to a temp spool before responding — a definite Content-Length and a real error
status, at the cost of latency and disk. It is deliberately not used because the
probability above does not justify that cost.

## Bounding runaway work

A read-only DB connection is held open for the whole client download. Three bounds
keep that from becoming a liability (`stream_database_query`, `views`):

- **`statement_timeout`** bounds a runaway per-batch scan.
- **`idle_in_transaction_session_timeout`** bounds a stalled client, so a vanished
  browser can't pin the transaction (and block VACUUM on the workspace DB) forever.
- **`_EXPORT_SLOTS`** (a `BoundedSemaphore`, size `DATA_STUDIO_EXPORT_MAX_CONCURRENCY`)
  bounds how many exports a single worker runs at once. It is per process, so the
  per-pod ceiling is this value × the gunicorn worker count; it is not a global cap
  (see the per-role Postgres `CONNECTION LIMIT` for that). Excess callers get an
  immediate **429** rather than being queued behind a backlog.

## Resource lifecycle

The slot and the DB connection are held for the whole client download, not just the
view call — the streaming response keeps consuming rows after the view returns. So
they are freed when the *stream* ends, via `async_streaming_csv_response`'s `on_finish`
callback, which fires exactly once on completion, mid-stream error and client
disconnect alike. The only paths that free them in the view itself are the ones that
never start streaming.

The disconnect case is the subtle one: an async generator's own `finally` runs only at
garbage-collection time when the client goes away, so cleanup hangs off Django's
deterministic `response.close()` instead (`_CleanupStreamingHttpResponse`). A once-guard
makes the overlap (normal completion reaches cleanup by two routes) safe.

## The "download began" signal (cookie handshake)

The browser hands a successful attachment to its download manager without navigating
the hidden iframe the frontend posts into, so the page has no `load` event to observe
that the download started. The backend signals it by setting a short-lived, JS-readable
cookie whose **name** carries the caller's token (`csvDownloadToken-<token>`); the
frontend polls for that exact name. A per-token name (rather than one shared cookie
holding the token as its value) keeps concurrent downloads from clobbering each other's
signal. Note it signals "began", not "completed" — a mid-stream failure cannot retract
it.

These cross-tier constants (cookie prefix, POST field names) are the one thing the two
tiers must agree on with no shared code path, so they live in a shared contract fixture
(`tests/fixtures/download_contract.json`) asserted on both sides — see `tests/test_views.py`
and `DataStudioEditor/downloadQueryCsv.test.ts`.

## A known, pre-existing limitation

Duplicate column names in a result (`SELECT a.id, b.id …`) collapse under
`RealDictCursor` — the CSV repeats one value. This affects the interactive path
identically and is not specific to the export.
