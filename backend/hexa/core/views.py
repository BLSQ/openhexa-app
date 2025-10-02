from logging import getLogger

from django.db import connection
from django.http import HttpRequest, HttpResponse, HttpResponseServerError

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
    EXCEPTION, UNCATCHED_EXCEPTION, ZERO_DIVISION, VALUE_ERROR.
    Use a GET parameter to specify message, default to "Test logger"

    Example: test_logger?level=INFO&message=Test1
    Example: test_logger?level=UNCATCHED_EXCEPTION&message=Test500Error
    Example: test_logger?level=ZERO_DIVISION (simulates real 500 error)

    :param request: HttpRequest request
    :return: HttpResponse web response
    """
    message = request.GET.get("message", "Test logger")
    level = request.GET.get("level", "INFO")
    if level not in (
        "INFO",
        "WARNING",
        "ERROR",
        "EXCEPTION",
        "UNCATCHED_EXCEPTION",
        "ZERO_DIVISION",
        "VALUE_ERROR",
    ):
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
    elif level == "ZERO_DIVISION":
        # Simulate a real programming error that would cause 500
        x = 1 / 0  # noqa: F841
    elif level == "VALUE_ERROR":
        # Simulate another common error type
        int("not_a_number")
    else:
        assert level == "UNCATCHED_EXCEPTION", "should never happen"
        raise Exception(message)

    return HttpResponse("ok")
