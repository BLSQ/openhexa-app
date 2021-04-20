from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from hexa.plugins.connector_airflow.models import ComposerEnvironment


def pipeline_environment_detail(request, pipeline_environment_id):
    pipeline_environment = get_object_or_404(
        ComposerEnvironment.objects.filter_for_user(request.user),
        pk=pipeline_environment_id,
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (
            pipeline_environment.display_name,
            "connector_airflow:pipeline_environment_detail",
            pipeline_environment_id,
        ),
    ]

    return render(
        request,
        "connector_airflow/pipeline_environment_detail.html",
        {
            "pipeline_environment": pipeline_environment,
            "breadcrumbs": breadcrumbs,
        },
    )


def pipeline_environment_sync(request, datasource_id):
    pipeline_environment = get_object_or_404(
        ComposerEnvironment.objects.filter_for_user(request.user), pk=datasource_id
    )
    sync_result = pipeline_environment.sync()
    messages.success(request, sync_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))
