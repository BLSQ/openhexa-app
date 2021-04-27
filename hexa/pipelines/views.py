from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from hexa.pipelines.models import PipelinesIndexType, PipelinesIndex


def index(request):
    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
    ]
    environment_indexes = PipelinesIndex.objects.filter_for_user(request.user).filter(
        index_type=PipelinesIndexType.PIPELINES_ENVIRONMENT.value
    )

    return render(
        request,
        "pipelines/index.html",
        {
            "environment_indexes": environment_indexes,
            "breadcrumbs": breadcrumbs,
        },
    )
