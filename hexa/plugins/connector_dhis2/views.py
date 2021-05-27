import json

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from hexa.catalog.lists import build_summary_list_params, build_paginated_list_params
from .models import Instance, Indicator, DataElement, Extract


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
    instance, data_element = _get_instance_and_data_element(
        request, instance_id, data_element_id
    )

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
        },
    )


@require_http_methods(["POST"])
def data_element_update(request, instance_id, data_element_id):
    instance, data_element = _get_instance_and_data_element(
        request, instance_id, data_element_id
    )

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


def data_element_extract(
    request, instance_id, data_element_id
):  # TODO: should be post + DRY indicators
    instance, data_element = _get_instance_and_data_element(
        request, instance_id, data_element_id
    )

    current_extract = _get_current_extract(request)
    current_extract.data_elements.add(data_element)
    current_extract.save()

    messages.success(
        request, _("Added data element to current extract"), extra_tags="green"
    )

    return redirect(request.META.get("HTTP_REFERER"))


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
    instance, indicator = _get_instance_and_indicator(
        request, instance_id, indicator_id
    )

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


@require_http_methods(["POST"])
def indicator_update(request, instance_id, indicator_id):
    instance, indicator = _get_instance_and_indicator(
        request, instance_id, indicator_id
    )

    update_data = json.loads(request.body)
    indicator.update(**update_data)

    return render(
        request,
        "connector_dhis2/components/indicator_card.html",
        {
            "instance": instance,
            "indicator": indicator,
        },
    )


def indicator_extract(
    request, instance_id, indicator_id
):  # TODO: should be post + DRY data elements
    instance, indicator = _get_instance_and_indicator(
        request, instance_id, indicator_id
    )

    current_extract = _get_current_extract(request)
    current_extract.indicators.add(indicator)
    current_extract.save()

    messages.success(
        request, _("Added indicator to current extract"), extra_tags="green"
    )

    return redirect(request.META.get("HTTP_REFERER"))


def instance_sync(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    sync_result = instance.sync(request.user)
    messages.success(request, sync_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))


def extract_detail(request, extract_id):
    extract = get_object_or_404(
        Extract.objects.filter_for_user(request.user), id=extract_id
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (extract.display_name,),
    ]

    return render(
        request,
        "connector_dhis2/extract_detail.html",
        {
            "extract": extract,
            "breadcrumbs": breadcrumbs,
        },
    )


def extract_delete(request, extract_id):
    extract = get_object_or_404(
        Extract.objects.filter_for_user(request.user), id=extract_id
    )
    extract.delete()

    messages.success(request, _("Delete current extract"), extra_tags="green")

    return redirect(reverse("catalog:index"))


def _get_current_extract(request):
    current_extract = None
    if request.session.get("connector_dhis2_current_extract") is not None:
        try:
            current_extract = Extract.objects.filter_for_user(request.user).get(
                id=request.session.get("connector_dhis2_current_extract")
            )
        except Extract.DoesNotExist:
            pass

    if current_extract is None:
        current_extract = Extract.objects.create(user=request.user)
        request.session["connector_dhis2_current_extract"] = str(current_extract.id)

    return current_extract


def _get_instance_and_data_element(request, instance_id, data_element_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )

    return instance, get_object_or_404(
        DataElement.objects.filter(instance=instance), pk=data_element_id
    )


def _get_instance_and_indicator(request, instance_id, indicator_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )

    return instance, get_object_or_404(
        Indicator.objects.filter(instance=instance), pk=indicator_id
    )
