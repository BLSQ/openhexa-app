import logging

from django.core.exceptions import RequestDataTooBig
from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.middleware.gzip import GZipMiddleware
from django.utils import timezone
from oauth2_provider.models import AccessToken

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("django.security.RequestDataTooBig")


PRECOMPRESSED_CONTENT_TYPES = frozenset(
    {
        "application/gzip",
        "application/pdf",
        "application/x-7z-compressed",
        "application/x-bzip2",
        "application/x-xz",
        "application/zip",
        "application/zstd",
        "font/woff",
        "font/woff2",
    }
)
PRECOMPRESSED_CONTENT_TYPE_PREFIXES = ("audio/", "image/", "video/")
COMPRESSIBLE_EXCEPTIONS = frozenset({"image/svg+xml"})
PRECOMPRESSED_EXTENSIONS = (
    ".br",
    ".fgb",
    ".gz",
    ".mbtiles",
    ".parquet",
    ".pmtiles",
    ".zst",
)


UNCOMPRESSIBLE_CONTENT_TYPES = frozenset({"text/event-stream"})


def response_content_type(response) -> str:
    return response.get("Content-Type", "").split(";")[0].strip().lower()


def is_precompressed(content_type: str, path: str) -> bool:
    """Whether the body is already compressed, so gzip would only cost CPU."""
    if content_type in COMPRESSIBLE_EXCEPTIONS:
        return False
    if content_type in PRECOMPRESSED_CONTENT_TYPES:
        return True
    if content_type.startswith(PRECOMPRESSED_CONTENT_TYPE_PREFIXES):
        return True
    return path.lower().endswith(PRECOMPRESSED_EXTENSIONS)


def is_partial(response) -> bool:
    return response.status_code == 206 or response.has_header("Content-Range")


def should_skip_compression(request, response) -> bool:
    """Whether gzipping this response would break it or gain nothing."""
    content_type = response_content_type(response)
    if content_type in UNCOMPRESSIBLE_CONTENT_TYPES:
        return True
    if is_partial(response):
        return True
    return is_precompressed(content_type, request.path)


class SSEAwareGZipMiddleware(GZipMiddleware):
    """GZipMiddleware that leaves a response alone when compressing it would hurt."""

    def process_response(self, request, response):
        if should_skip_compression(request, response):
            return response
        return super().process_response(request, response)


class RequestTooBigMiddleware:
    """Convert RequestDataTooBig into a 413 JSON response.

    Uses process_exception so Django's built-in SuspiciousOperation handling
    (which would convert to a generic 400) doesn't run first. Re-emits the
    security log Django would have produced so Sentry's LoggingIntegration
    still captures the event without us touching sentry_sdk.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exception: Exception):
        if not isinstance(exception, RequestDataTooBig):
            return None
        security_logger.error(
            str(exception),
            exc_info=exception,
            extra={"status_code": 413, "request": request},
        )
        return JsonResponse({"error": "REQUEST_TOO_LARGE"}, status=413)


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


def oauth2_token_authentication_middleware(get_response):
    def middleware(request: HttpRequest):
        if request.user.is_authenticated:
            return get_response(request)

        try:
            auth_type, token = request.headers["Authorization"].split(" ")
            if auth_type.lower() == "bearer":
                access_token = AccessToken.objects.select_related("user").get(
                    token=token
                )
                if (
                    access_token.expires >= timezone.now()
                    and request.path.startswith("/mcp")
                    and "openhexa:mcp" in access_token.scope
                ):  # Only allow MCP access for now, users authorized this scope for MCP access, not for GraphQL or other endpoints. We can later add more scopes for other endpoints if needed.
                    request.user = access_token.user
        except KeyError:
            pass
        except ValueError:
            logger.error("OAuth2 token authentication error")
        except AccessToken.DoesNotExist:
            pass

        return get_response(request)

    return middleware
