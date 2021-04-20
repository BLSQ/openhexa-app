from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from hexa.plugins.connector_airflow.models import Environment


def environment_detail(request, environment_id):
    environment = get_object_or_404(
        Environment.objects.filter_for_user(request.user),
        pk=environment_id,
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (
            environment.display_name,
            "connector_airflow:environment_detail",
            environment_id,
        ),
    ]

    return render(
        request,
        "connector_airflow/environment_detail.html",
        {
            "environment": environment,
            "breadcrumbs": breadcrumbs,
        },
    )


def environment_sync(request, datasource_id):
    environment = get_object_or_404(
        Environment.objects.filter_for_user(request.user), pk=datasource_id
    )
    sync_result = environment.sync()
    messages.success(request, sync_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))
