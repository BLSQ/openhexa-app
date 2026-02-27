import logging

from django.db import connection
from django.http import HttpRequest
from django.utils import timezone
from oauth2_provider.models import AccessToken

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
                if access_token.expires >= timezone.now():
                    request.user = access_token.user
        except KeyError:
            pass
        except ValueError:
            logger.error("OAuth2 token authentication error")
        except AccessToken.DoesNotExist:
            pass

        return get_response(request)

    return middleware
