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

from hexa.core.csv import buffered_csv_response
from hexa.workspaces.models import Workspace

from .utils import MultipleStatementsError, stream_database_query

# The download-correlation token is echoed back as part of a Set-Cookie *name*,
# so it is constrained to characters that are safe there and cannot break the
# header. A token failing this is simply ignored (the frontend then times out
# rather than misreading another download's signal).
_DOWNLOAD_TOKEN_RE = re.compile(r"[A-Za-z0-9-]{1,64}")

# Per-process admission control (see settings.DATA_STUDIO_EXPORT_MAX_CONCURRENCY).
# A full-result export is far heavier and longer-lived than an interactive query,
# so an unbounded number of concurrent downloads could pile up threads, read-only
# DB connections and spooled buffers in a single worker. Callers that cannot get a
# slot are turned away immediately with a 429 rather than queued, so they fail
# fast instead of holding a request open behind a backlog.
_EXPORT_SLOTS = threading.BoundedSemaphore(settings.DATA_STUDIO_EXPORT_MAX_CONCURRENCY)


@require_POST
def download_query_csv(request: HttpRequest, workspace_slug: str) -> HttpResponse:
    """Export the full result of a Data Studio SQL query as a CSV download.

    The row cap used by the interactive editor is deliberately not applied here:
    the point of the download is to get the entire result set. See
    :func:`hexa.databases.utils.stream_database_query`.

    The whole result is serialised into a spooled temp file *before* the response
    is sent (see :func:`hexa.core.csv.buffered_csv_response`), so a failure mid
    query — a statement timeout on a large scan, a dropped connection — returns a
    clean HTTP 400 instead of a silently truncated file. The cost is that the
    user waits for the query to fully run and serialise before the browser's
    download begins. Rough guide (dominated by query execution, then ~1M
    cells/s of serialisation; assumes ~10 narrow columns):

        result size        rows        approx. wait      approx. file
        small              ≤ 10k       < 1 s             ≤ ~2 MB
        medium             ~100k       ~1–4 s            ~15–25 MB
        large              ~1M         ~15–45 s          ~150–250 MB
        very large         ~5M+        minutes; risks the 5-min statement timeout

    Real numbers vary widely with query complexity, column count and value
    widths; the query's own execution time (unbounded up to the statement
    timeout) usually dwarfs serialisation. Peak server memory stays bounded (the
    buffer spills to disk); the temp file's disk footprint tracks the file size
    above for the download's lifetime.
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
    # For the buffered response the slot covers the whole heavy phase: the result
    # is fully materialised into a temp file below, so once this block returns the
    # DB connection is already closed and only the cheap spool->client transfer
    # remains — releasing here is correct. When this endpoint switches to a true
    # streaming response the connection stays open for the entire client download,
    # so the release must move into the row generator's `finally` instead.
    try:
        # Both the query execution and the full row fetch happen inside this block
        # (buffered_csv_response consumes the generator eagerly), so a failure at
        # any point — including mid-scan — is caught here and turned into a 400
        # before a single byte of the attachment is sent.
        try:
            columns, row_dicts = stream_database_query(workspace, query)
            rows = ([row[column] for column in columns] for row in row_dicts)
            response = buffered_csv_response(
                header=columns, rows=rows, filename="query-results.csv"
            )
        except MultipleStatementsError:
            return HttpResponseBadRequest("Only a single SQL statement is allowed.")
        except Psycopg2Error:
            return HttpResponseBadRequest("The query could not be executed.")

        # The browser hands a successful attachment to its download manager without
        # navigating the hidden iframe the frontend posts into, so the page has no
        # way to observe that the download started. Signal it with a short-lived,
        # JS-readable cookie whose *name* carries the caller's token, set the moment
        # the response headers go out; the frontend polls for that exact name to
        # tell "download began" apart from an error page (which does navigate the
        # iframe). A per-token name — rather than one shared cookie holding the
        # token as its value — keeps concurrent downloads from clobbering each
        # other's signal. See frontend downloadQueryCsv.ts.
        download_token = request.POST.get("download_token")
        if download_token and _DOWNLOAD_TOKEN_RE.fullmatch(download_token):
            response.set_cookie(
                f"csvDownloadToken-{download_token}", "1", max_age=120, samesite="Lax"
            )
        return response
    finally:
        _EXPORT_SLOTS.release()
