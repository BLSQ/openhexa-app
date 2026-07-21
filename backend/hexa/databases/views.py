import logging
import re
import threading

from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.views.decorators.http import require_POST
from psycopg2 import Error as Psycopg2Error

from hexa.core.csv import async_streaming_csv_response
from hexa.workspaces.models import Workspace

from .utils import MultipleStatementsError, stream_database_query

logger = logging.getLogger(__name__)

# The download-correlation token is echoed back as part of a Set-Cookie *name*,
# so it is constrained to characters that are safe there and cannot break the
# header. A token failing this is simply ignored (the frontend then times out
# rather than misreading another download's signal).
_DOWNLOAD_TOKEN_RE = re.compile(r"[A-Za-z0-9-]{1,64}")

# Per-process admission control (see settings.DATA_STUDIO_EXPORT_MAX_CONCURRENCY).
# A full-result export is far heavier and longer-lived than an interactive query
# — the streaming response below holds a read-only DB connection open for the
# whole client download — so an unbounded number of concurrent downloads could
# pile up connections and threads in a single worker. Callers that cannot get a
# slot are turned away immediately with a 429 rather than queued, so they fail
# fast instead of holding a request open behind a backlog.
_EXPORT_SLOTS = threading.BoundedSemaphore(settings.DATA_STUDIO_EXPORT_MAX_CONCURRENCY)


def _next_projected_batch(batch_iter, columns):
    """Pull the next batch off a blocking cursor and project it to ``columns``.

    Returns ``None`` once the cursor is exhausted. Called through
    ``sync_to_async`` (see :func:`_tracked_row_batches`) so the blocking
    ``fetchmany`` and the projection both run in a worker thread rather than on
    the event loop.
    """
    batch = next(batch_iter, None)
    if batch is None:
        return None
    return [[row[column] for column in columns] for row in batch]


async def _tracked_row_batches(batch_iter, columns, *, workspace, user):
    """Yield projected row batches, recording a failure HTTP can no longer report.

    The underlying cursor is blocking psycopg2, so each fetch is run off the event
    loop via ``sync_to_async(thread_sensitive=False)``; the async CSV response can
    then stream batch by batch without stalling the worker's event loop.

    Once the streaming response has sent its headers the status is fixed at 200,
    so a query that fails partway through the scan (a statement timeout on a big
    table, a dropped connection) can only end the download truncated — it cannot
    become an error status the client would notice. Log it here, where the failure
    actually surfaces, so a silently short file is at least visible on the server.
    A client that simply goes away raises ``GeneratorExit`` (a ``BaseException``,
    not caught below), so an expected disconnect is left unlogged.

    Closing ``batch_iter`` (which runs the cursor/connection teardown) is *not*
    done here: on a client disconnect this generator's ``finally`` would only run
    at garbage-collection time, so the connection is instead closed by the
    response's ``on_finish`` callback, which fires deterministically on completion,
    error and disconnect alike (see :func:`download_query_csv`).
    """
    fetched = 0
    try:
        while True:
            batch = await sync_to_async(_next_projected_batch, thread_sensitive=False)(
                batch_iter, columns
            )
            if batch is None:
                break
            fetched += len(batch)
            yield batch
    except Exception:
        logger.warning(
            "Data Studio CSV export stream aborted after %d rows "
            "(workspace=%s, user=%s)",
            fetched,
            workspace.slug,
            getattr(user, "id", None),
            exc_info=True,
        )
        raise


@require_POST
def download_query_csv(request: HttpRequest, workspace_slug: str) -> HttpResponse:
    """Export the full result of a Data Studio SQL query as a streaming CSV download.

    The row cap used by the interactive editor is deliberately not applied here:
    the point of the download is to get the entire result set. See
    :func:`hexa.databases.utils.stream_database_query`.

    The result is streamed batch by batch
    (:func:`hexa.core.csv.async_streaming_csv_response`) rather than buffered, so
    bytes reach the browser as soon as the query starts producing them: a large
    export is neither delayed by full serialisation nor exposed to a proxy
    idle-timeout while nothing is sent. The response is an *async* stream on
    purpose — under the ASGI worker a sync stream would be silently drained into
    memory in one go (``StreamingHttpResponse.__aiter__`` falls back to
    ``sync_to_async(list)``), so the blocking cursor fetches are pushed off the
    event loop instead (see :func:`_tracked_row_batches`).

    The query is executed and its first batch fetched *before* the response is
    built (``stream_database_query`` is eager), so the common failures — invalid
    SQL, a permission error, an empty statement — still surface here as a clean
    HTTP 400 before a single byte is sent. The trade-off of streaming is that a
    failure *after* the first batch (a statement timeout mid-scan, a dropped
    connection) can no longer change the already-sent 200 status: the download
    just ends truncated. Such failures are logged (see
    :func:`_tracked_row_batches`) so they stay observable server-side.

    How likely is a silently-truncated download?
    --------------------------------------------
    Low, by design, and the residual causes are infrastructural rather than
    query-shaped:

    * **Front-loaded query cost is caught, not truncated.** The first batch is
      fetched eagerly, so any query whose cost is paid up front — a sort, a hash
      aggregate, a large join that must materialise before the first row — fails
      during that eager fetch and becomes a clean HTTP 400. Only a query that is
      *cheap to start and expensive to sustain* (a plain streaming scan) can get
      past the first byte and then fail.

    * **statement_timeout bounds a single batch, not the whole scan.** With the
      server-side named cursor each ``FETCH`` is its own statement, so the
      5-minute ``DOWNLOAD_QUERY_TIMEOUT_MS`` limits one ``DOWNLOAD_QUERY_BATCH_SIZE``
      batch — not the total download. A legitimately long export (many minutes of
      steady streaming) never trips it as long as each individual batch returns
      within 5 minutes; only a pathologically slow *per-batch* scan would.

    * **idle_in_transaction fires only on a stalled client.** The 5-minute
      ``DOWNLOAD_QUERY_IDLE_TIMEOUT_MS`` aborts the transaction only if the client
      stops consuming for that long mid-stream — by which point the user's own
      download has visibly stalled anyway, so a truncated file is not a silent
      surprise.

    That leaves genuine infra events as the realistic causes: the workspace DB
    connection dropping (a restart, failover, or network blip) or this web worker
    being killed mid-stream (a deploy, an OOM, or a scale-down that outlasts
    gunicorn's graceful-shutdown window). These are infrequent and usually visible
    through other signals (deploy notices, error rates), not only through a short
    CSV.

    When it does happen the impact is a CSV that opens cleanly but is missing its
    trailing rows, with no client-side error. What mitigates it is the server-side
    WARNING log above (row count, workspace, user). (This stream is served
    uncompressed — ``SSEAwareGZipMiddleware`` skips async streams because Django
    5.2 would gzip them one member per chunk, which browsers can't reliably decode;
    revisit once on Django 6.0. So there is no gzip layer to also flag a truncated
    body, and no Content-Length either.) If silent truncation ever proves to matter
    in practice, the fallback is to buffer the whole CSV to a temp spool before
    responding (a definite Content-Length and a real error status, at the cost of
    latency and disk); it is deliberately not used here because the probability
    above does not justify that cost.

    A read-only DB connection is held open for the whole download; a statement
    timeout and an idle-in-transaction timeout bound a runaway scan and a stalled
    client respectively, and ``_EXPORT_SLOTS`` bounds how many such downloads a
    single worker runs at once (excess callers get a 429).
    """
    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        raise Http404("Workspace not found")

    if not request.user.has_perm("databases.run_query", workspace):
        return HttpResponseForbidden(
            "You are not allowed to run queries on this workspace."
        )

    query = (request.POST.get("query") or "").strip()
    if not query:
        return HttpResponseBadRequest("A query is required.")

    # Only genuine work should consume a slot, so acquire it after the cheap
    # request checks above and turn a full pool away with a 429.
    if not _EXPORT_SLOTS.acquire(blocking=False):
        return HttpResponse(
            "Too many exports are running right now. Please try again in a moment.",
            status=429,
        )
    # The slot and the DB connection are held for the whole client download, not
    # just this view call: the streaming response keeps consuming rows after the
    # view returns. So free them when the *stream* ends — via
    # async_streaming_csv_response's on_finish, which fires exactly once on
    # completion, mid-stream error and client disconnect alike — and only free them
    # here on the paths that never start streaming.
    handed_off_to_stream = False
    try:
        # stream_database_query runs the query and fetches its first batch eagerly,
        # so an invalid statement raises here and becomes a 400 before any byte is
        # sent. A failure later, mid-scan, cannot: see the docstring.
        try:
            columns, db_batches = stream_database_query(workspace, query)
        except MultipleStatementsError:
            return HttpResponseBadRequest("Only a single SQL statement is allowed.")
        except Psycopg2Error:
            return HttpResponseBadRequest("The query could not be executed.")

        def release_export() -> None:
            # Closing db_batches runs the cursor/connection teardown; do it first
            # so the connection is freed even if the query is still mid-scan (a
            # disconnect), then always hand the slot back. on_finish guarantees
            # this runs once, so a double close/release cannot happen.
            try:
                db_batches.close()
            finally:
                _EXPORT_SLOTS.release()

        response = async_streaming_csv_response(
            header=columns,
            row_batches=_tracked_row_batches(
                db_batches, columns, workspace=workspace, user=request.user
            ),
            filename="query-results.csv",
            on_finish=release_export,
        )

        # The browser hands a successful attachment to its download manager without
        # navigating the hidden iframe the frontend posts into, so the page has no
        # way to observe that the download started. Signal it with a short-lived,
        # JS-readable cookie whose *name* carries the caller's token, set on the
        # response headers (which flush as streaming begins); the frontend polls
        # for that exact name to tell "download began" apart from an error page
        # (which does navigate the iframe). A per-token name — rather than one
        # shared cookie holding the token as its value — keeps concurrent downloads
        # from clobbering each other's signal. Note this signals "began", not
        # "completed": a mid-stream failure cannot retract it (see the docstring).
        # See frontend downloadQueryCsv.ts.
        download_token = request.POST.get("download_token")
        if download_token and _DOWNLOAD_TOKEN_RE.fullmatch(download_token):
            response.set_cookie(
                f"csvDownloadToken-{download_token}", "1", max_age=120, samesite="Lax"
            )
        handed_off_to_stream = True
        return response
    finally:
        if not handed_off_to_stream:
            _EXPORT_SLOTS.release()
