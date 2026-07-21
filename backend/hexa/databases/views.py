import logging
import re
import threading

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

from hexa.core.csv import streaming_csv_response
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


def _tracked_rows(row_dicts, columns, *, workspace, user):
    """Project rows to ``columns``, recording a failure HTTP can no longer report.

    Once the streaming response has sent its headers the status is fixed at 200,
    so a query that fails partway through the scan (a statement timeout on a big
    table, a dropped connection) can only end the download truncated — it cannot
    become an error status the client would notice. Log it here, where the
    failure actually surfaces, so a silently short file is at least visible on the
    server. A client that simply goes away (GeneratorExit) is expected, not a
    failure, and is left unlogged.
    """
    fetched = 0
    try:
        for row in row_dicts:
            fetched += 1
            yield [row[column] for column in columns]
    except GeneratorExit:
        raise
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

    The result is streamed row by row (:func:`hexa.core.csv.streaming_csv_response`)
    rather than buffered, so bytes reach the browser as soon as the query starts
    producing them: a large export is neither delayed by full serialisation nor
    exposed to a proxy idle-timeout while nothing is sent.

    The query is executed and its first batch fetched *before* the response is
    built (``stream_database_query`` is eager), so the common failures — invalid
    SQL, a permission error, an empty statement — still surface here as a clean
    HTTP 400 before a single byte is sent. The trade-off of streaming is that a
    failure *after* the first batch (a statement timeout mid-scan, a dropped
    connection) can no longer change the already-sent 200 status: the download
    just ends truncated. Such failures are logged (see :func:`_tracked_rows`) so
    they stay observable server-side.

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
    # The slot (and the DB connection) are held for the whole client download, not
    # just this view call: the streaming response keeps consuming rows after the
    # view returns. So release the slot when the *stream* ends — via
    # streaming_csv_response's on_finish, which fires on completion, mid-stream
    # error and client disconnect alike — and only release here on the paths that
    # never start streaming.
    handed_off_to_stream = False
    try:
        # stream_database_query runs the query and fetches its first batch eagerly,
        # so an invalid statement raises here and becomes a 400 before any byte is
        # sent. A failure later, mid-scan, cannot: see the docstring.
        try:
            columns, row_dicts = stream_database_query(workspace, query)
        except MultipleStatementsError:
            return HttpResponseBadRequest("Only a single SQL statement is allowed.")
        except Psycopg2Error:
            return HttpResponseBadRequest("The query could not be executed.")

        response = streaming_csv_response(
            header=columns,
            rows=_tracked_rows(
                row_dicts, columns, workspace=workspace, user=request.user
            ),
            filename="query-results.csv",
            on_finish=_EXPORT_SLOTS.release,
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
