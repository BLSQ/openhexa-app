import logging

from django.db import connection
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def set_remote_addr_from_forwarded_for(get_response):
    """Set the REMOTE_ADDR from the HTTP_X_FORWARDED_FOR header."""

    def middleware(request: HttpRequest):
        try:
            real_ip = request.META["HTTP_X_FORWARDED_FOR"]
        except KeyError:
            pass
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # Take just the first one.
            real_ip = real_ip.split(",")[0]
            request.META["REMOTE_ADDR"] = real_ip

        return get_response(request)

    return middleware


def query_count_debug_middleware(get_response):
    """Debug middleware to log the number of SQL queries per request."""

    def middleware(request: HttpRequest):
        initial_queries = len(connection.queries)
        response = get_response(request)
        queries_count = len(connection.queries) - initial_queries
        if queries_count > 20:
            logger.warning(
                f"High query count: {queries_count} queries for {request.method} {request.path}"
            )

            if request.path == "/graphql/" and hasattr(request, "body"):
                try:
                    import json

                    body = json.loads(request.body.decode("utf-8"))
                    operation_name = body.get("operationName", "unknown")
                    logger.warning(f"GraphQL operation: {operation_name}")
                except Exception:
                    pass
        response["X-DB-Query-Count"] = str(queries_count)
        return response

    return middleware
