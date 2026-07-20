import re

from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.views.decorators.http import require_POST
from psycopg2 import Error as Psycopg2Error

from hexa.core.csv import stream_csv
from hexa.workspaces.models import Workspace

from .utils import MultipleStatementsError, stream_database_query

# The download-correlation token is echoed back as part of a Set-Cookie *name*,
# so it is constrained to characters that are safe there and cannot break the
# header. A token failing this is simply ignored (the frontend then times out
# rather than misreading another download's signal).
_DOWNLOAD_TOKEN_RE = re.compile(r"[A-Za-z0-9-]{1,64}")


@require_POST
def download_query_csv(request: HttpRequest, workspace_slug: str) -> HttpResponse:
    """Stream the full result of a Data Studio SQL query as a CSV download.

    The row cap used by the interactive editor is deliberately not applied here:
    the point of the download is to get the entire result set. See
    :func:`hexa.databases.utils.stream_database_query`.
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

    try:
        columns, row_dicts = stream_database_query(workspace, query)
    except MultipleStatementsError:
        return HttpResponseBadRequest("Only a single SQL statement is allowed.")
    except Psycopg2Error:
        return HttpResponseBadRequest("The query could not be executed.")

    rows = ([row[column] for column in columns] for row in row_dicts)
    response = stream_csv(header=columns, rows=rows, filename="query-results.csv")

    # The browser hands a successful attachment to its download manager without
    # navigating the hidden iframe the frontend posts into, so the page has no
    # way to observe that the download started. Signal it with a short-lived,
    # JS-readable cookie whose *name* carries the caller's token, set the moment
    # the response headers go out; the frontend polls for that exact name to tell
    # "download began" apart from an error page (which does navigate the iframe).
    # A per-token name — rather than one shared cookie holding the token as its
    # value — keeps concurrent downloads from clobbering each other's signal.
    # See frontend downloadQueryCsv.ts.
    download_token = request.POST.get("download_token")
    if download_token and _DOWNLOAD_TOKEN_RE.fullmatch(download_token):
        response.set_cookie(
            f"csvDownloadToken-{download_token}", "1", max_age=120, samesite="Lax"
        )
    return response
