from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from hexa.plugins.connector_airflow.models import ComposerEnvironment


def pipeline_server_detail(request, pipeline_server_id):
    pipeline_server = get_object_or_404(
        ComposerEnvironment.objects.filter_for_user(request.user), pk=pipeline_server_id
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (
            pipeline_server.display_name,
            "connector_airflow:pipeline_server_detail",
            pipeline_server_id,
        ),
    ]

    return render(
        request,
        "connector_airflow/pipeline_server_detail.html",
        {
            "pipeline_server": pipeline_server,
            "breadcrumbs": breadcrumbs,
        },
    )


def pipeline_server_sync(request, datasource_id):
    pipeline_server = get_object_or_404(
        ComposerEnvironment.objects.filter_for_user(request.user), pk=datasource_id
    )
    sync_result = pipeline_server.sync()
    messages.success(request, sync_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))
