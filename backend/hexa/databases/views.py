import logging
import re
import threading
from contextlib import ExitStack

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

# The token is echoed back inside a Set-Cookie *name*, so restrict it to characters
# safe there. A token failing this is ignored (the frontend then times out rather
# than misreading another download's signal).
_DOWNLOAD_TOKEN_RE = re.compile(r"[A-Za-z0-9-]{1,64}")

# Per-process admission control (settings.DATA_STUDIO_EXPORT_MAX_CONCURRENCY): each
# export holds a read-only connection open for the whole download, so an unbounded
# number would pile up connections and threads in one worker. Excess callers get a 429
# immediately rather than queueing behind a backlog. See the app README.
_EXPORT_SLOTS = threading.BoundedSemaphore(settings.DATA_STUDIO_EXPORT_MAX_CONCURRENCY)


def _next_projected_batch(batch_iter, columns):
    """Pull the next batch off the blocking cursor and project it to ``columns``.

    Returns ``None`` once exhausted. Run through ``sync_to_async`` (see
    :func:`_tracked_row_batches`) so the blocking fetch and projection stay off the
    event loop.
    """
    batch = next(batch_iter, None)
    if batch is None:
        return None
    return [[row[column] for column in columns] for row in batch]


async def _tracked_row_batches(batch_iter, columns, *, workspace, user):
    """Yield projected row batches, logging a mid-stream failure HTTP can no longer report.

    Each fetch runs off the event loop via ``sync_to_async(thread_sensitive=False)``
    since the cursor is blocking psycopg2. Once headers are sent the status is fixed at
    200, so a failure partway through the scan can only truncate the download; it is
    logged here, where it surfaces, so a short file stays visible server-side. A client
    that goes away raises ``GeneratorExit`` (a ``BaseException``, not caught here), so an
    expected disconnect is left unlogged. Closing ``batch_iter`` is left to the response's
    ``on_finish`` (see :func:`download_query_csv`), which fires deterministically on
    disconnect where this generator's ``finally`` would wait on GC.
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

    No row cap is applied — the point is the whole result set. The result is streamed
    batch by batch (:func:`hexa.core.csv.async_streaming_csv_response`), async and off
    the event loop, rather than buffered; the app README covers why streaming, why
    async, and the memory/timeout bounds.

    ``stream_database_query`` runs the query and fetches its first batch eagerly, so the
    common failures (invalid SQL, permission error, empty statement) surface here as a
    clean HTTP 400 before any byte is sent. The trade-off: a failure *after* the first
    batch cannot change the already-sent 200 status — the download ends truncated
    (logged in :func:`_tracked_row_batches`). The README covers how likely that is and
    why it is accepted rather than buffered around.

    A read-only connection is held open for the whole download; ``statement_timeout``,
    ``idle_in_transaction_session_timeout`` and ``_EXPORT_SLOTS`` bound a runaway scan, a
    stalled client and per-worker concurrency respectively (excess callers get a 429).
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

    # Acquire only after the cheap request checks above; a full pool turns callers
    # away with a 429 rather than queueing them.
    if not _EXPORT_SLOTS.acquire(blocking=False):
        return HttpResponse(
            "Too many exports are running right now. Please try again in a moment.",
            status=429,
        )
    # The slot and connection outlive this view call — the stream keeps consuming
    # rows after it returns — so a single teardown (close the DB connection, then
    # hand the slot back; LIFO) owns both. It runs from the stream's on_finish once
    # streaming has started, and from this view's finally otherwise, so nothing
    # leaks even if building the response raises before the stream takes over.
    # ExitStack.close() is a no-op after its first call, and only one of the two
    # sites ever runs it (gated by handed_off_to_stream), so it fires exactly once.
    cleanup = ExitStack()
    cleanup.callback(_EXPORT_SLOTS.release)
    handed_off_to_stream = False
    try:
        try:
            columns, db_batches = stream_database_query(workspace, query)
        except MultipleStatementsError:
            return HttpResponseBadRequest("Only a single SQL statement is allowed.")
        except Psycopg2Error:
            return HttpResponseBadRequest("The query could not be executed.")
        cleanup.callback(db_batches.close)

        response = async_streaming_csv_response(
            header=columns,
            row_batches=_tracked_row_batches(
                db_batches, columns, workspace=workspace, user=request.user
            ),
            filename="query-results.csv",
            on_finish=cleanup.close,
        )

        # A successful attachment never navigates the iframe the frontend posts into,
        # so the page can't see the download start. Signal it with a short-lived,
        # JS-readable cookie whose *name* carries the caller's token (per-token, so
        # concurrent downloads don't clobber each other). Signals "began", not
        # "completed". See the app README and frontend downloadQueryCsv.ts.
        download_token = request.POST.get("download_token")
        if download_token and _DOWNLOAD_TOKEN_RE.fullmatch(download_token):
            response.set_cookie(
                f"csvDownloadToken-{download_token}", "1", max_age=120, samesite="Lax"
            )
        handed_off_to_stream = True
        return response
    finally:
        if not handed_off_to_stream:
            cleanup.close()
