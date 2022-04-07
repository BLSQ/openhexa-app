from logging import getLogger

from django.contrib.auth import authenticate, login
from django.db import connection
from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import Index
from hexa.core.activities import Activity, ActivityList
from hexa.core.datagrids import ActivityGrid
from hexa.core.models.behaviors import Status
from hexa.plugins.app import get_connector_app_configs
from hexa.plugins.connector_airflow.models import DAG
from hexa.plugins.connector_s3.models import Object

logger = getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(reverse("core:dashboard"))

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        next_url = request.POST["next"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect(next_url)
        else:
            errors = True
    else:
        errors = False
        next_url = request.GET.get("next", reverse("core:dashboard"))

    return render(request, "core/index.html", {"errors": errors, "next_url": next_url})


def dashboard(request: HttpRequest) -> HttpResponse:
    breadcrumbs = [(_("Dashboard"), "core:dashboard")]
    accessible_datasources = Index.objects.filter_for_user(request.user).roots()

    # TODO: We should instead filter on "executable file"-like on the index to avoid referencing a plugin here
    accessible_notebooks = Object.objects.filter(
        key__iendswith=".ipynb"
    ).filter_for_user(request.user)

    # Build latest activity
    last_activities = ActivityList(
        [
            Activity(
                occurred_at=timezone.now().replace(hour=0, minute=0),
                description=_("All datasources are up to date!"),
                status=Status.SUCCESS,
                url=reverse("catalog:index"),
            )
        ]
    )
    for app_config in get_connector_app_configs():
        last_activities += app_config.get_last_activities(request)

    last_activity_grid = ActivityGrid(
        last_activities, paginate=False, request=request, per_page=10
    )

    return render(
        request,
        "core/dashboard.html",
        {
            "counts": {
                "datasources": accessible_datasources.count(),
                "notebooks": accessible_notebooks.count(),
                "pipelines": DAG.objects.filter_for_user(request.user).count(),
            },
            "last_activity_grid": last_activity_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


def collections(request: HttpRequest) -> HttpResponse:
    """
    Returns an empty page in development when running without the new frontend.
    """
    return HttpResponse()


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
