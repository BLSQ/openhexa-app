import json

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from hexa.catalog.lists import build_summary_list_params, build_paginated_list_params
from .models import Instance


def instance_detail(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
    ]

    return render(
        request,
        "connector_dhis2/instance_detail.html",
        {
            "instance": instance,
            "data_elements_list_params": build_summary_list_params(
                instance.dataelement_set.all(),
                title=_("Data elements"),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                paginated_list_url=reverse(
                    "connector_dhis2:data_element_list",
                    kwargs={"instance_id": instance_id},
                ),
                item_name=_("data element"),
                item_template="connector_dhis2/components/data_element_list_item.html",
            ),
            "indicators_list_params": build_summary_list_params(
                instance.indicator_set.all(),
                title=_("Indicators"),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                paginated_list_url=reverse(
                    "connector_dhis2:indicator_list",
                    kwargs={"instance_id": instance_id},
                ),
                item_name=_("indicator"),
                item_template="connector_dhis2/components/indicator_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_list(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
        (_("Data Elements"),),
    ]

    return render(
        request,
        "connector_dhis2/data_element_list.html",
        {
            "instance": instance,
            "data_elements_list_params": build_paginated_list_params(
                instance.dataelement_set.all(),
                title=_("Data elements"),
                page_number=int(request.GET.get("page", "1")),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                item_name=_("data element"),
                item_template="connector_dhis2/components/data_element_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_detail(request, instance_id, data_element_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    data_element = get_object_or_404(instance.dataelement_set, pk=data_element_id)
    content_type_key = ContentType.objects.get_for_model(data_element).natural_key()

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
        (_("Data Elements"), "connector_dhis2:data_element_list", instance_id),
        (data_element.display_name,),
    ]

    return render(
        request,
        "connector_dhis2/data_element_detail.html",
        {
            "instance": instance,
            "data_element": data_element,
            "breadcrumbs": breadcrumbs,
            "content_type_key": ".".join(content_type_key),
            "object_id": data_element.id,
        },
    )


@require_http_methods(["POST"])
def data_element_update(request, instance_id, data_element_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    data_element = get_object_or_404(instance.dataelement_set, pk=data_element_id)

    update_data = json.loads(request.body)
    data_element.update(**update_data)

    return render(
        request,
        "connector_dhis2/components/data_element_card.html",
        {
            "instance": instance,
            "data_element": data_element,
        },
    )


def indicator_list(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
        (_("Indicators"),),
    ]

    return render(
        request,
        "connector_dhis2/indicator_list.html",
        {
            "instance": instance,
            "indicators_list_params": build_paginated_list_params(
                instance.indicator_set.all(),
                title=_("Indicators"),
                page_number=int(request.GET.get("page", "1")),
                columns=[
                    _("Name"),
                    _("Code"),
                    _("Values"),
                    _("Tags"),
                    _("Last update"),
                ],
                item_name=_("indicator"),
                item_template="connector_dhis2/components/indicator_list_item.html",
            ),
            "breadcrumbs": breadcrumbs,
        },
    )


def indicator_detail(request, instance_id, indicator_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    indicator = get_object_or_404(instance.indicator_set, pk=indicator_id)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
        (_("Indicators"), "connector_dhis2:indicator_list", instance_id),
        (indicator.display_name,),
    ]

    return render(
        request,
        "connector_dhis2/indicator_detail.html",
        {
            "instance": instance,
            "indicator": indicator,
            "breadcrumbs": breadcrumbs,
        },
    )


def instance_sync(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    sync_result = instance.sync()
    messages.success(request, sync_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))
