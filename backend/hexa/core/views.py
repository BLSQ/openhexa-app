from logging import getLogger

from django.db import connection
from django.http import HttpRequest, HttpResponse, HttpResponseServerError, JsonResponse

logger = getLogger(__name__)


def ready(request: HttpRequest) -> HttpResponse:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            expected = (1,)
            if row != expected:
                return HttpResponseServerError(
                    f"Error: invalid database response (is `{row}`, should be `{expected}`)"
                )
    except Exception as e:
        return HttpResponseServerError(f"Error: can not connect to the database ({e})")

    return HttpResponse("ok")


def test_logger(request: HttpRequest) -> HttpResponse:
    """
    Generate a log to test logging setup.

    Use a GET parameter to specify level, default to INFO if absent. Value can be INFO, WARNING, ERROR,
    EXCEPTION, UNCATCHED_EXCEPTION.
    Use a GET parameter to specify message, default to "Test logger"

    Example: test_logger?level=INFO&message=Test1

    :param request: HttpRequest request
    :return: HttpResponse web response
    """
    message = request.GET.get("message", "Test logger")
    level = request.GET.get("level", "INFO")
    if level not in ("INFO", "WARNING", "ERROR", "EXCEPTION", "UNCATCHED_EXCEPTION"):
        level = "INFO"

    if level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "EXCEPTION":
        try:
            raise Exception(message)
        except Exception:
            logger.exception("test_logger")
    else:
        assert level == "UNCATCHED_EXCEPTION", "should never happen"
        raise Exception(message)

    return HttpResponse("ok")


def jwks(request: HttpRequest) -> JsonResponse:
    """
    Serve the JSON Web Key Set (JWKS) containing public keys for JWT verification.

    Returns the public key information from the configured RSA private key in JWKS format.
    This endpoint is used by external services to verify JWT tokens issued by OpenHEXA.

    If no private key is configured, returns an empty key set.

    :param request: HttpRequest
    :return: JsonResponse with JWKS data
    """
    from hexa.workspaces.jwt_utils import JWTConfigurationError, get_jwks

    try:
        jwks_data = get_jwks()
        if jwks_data is None:
            return JsonResponse({"keys": []})
        return JsonResponse(jwks_data)
    except JWTConfigurationError as e:
        logger.error(f"JWKS configuration error: {e}")
        return JsonResponse({"keys": []}, status=200)
