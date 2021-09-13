import json

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from .datagrids import DataElementGrid, IndicatorGrid, DatasetGrid
from .datacards import InstanceCard, DataElementCard, IndicatorCard, DatasetCard
from .models import Instance, Indicator, DataElement, Extract, DataSet


def instance_detail(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    instance_card = InstanceCard(instance, request=request)
    if request.method == "POST" and instance_card.save():
        return redirect(request.META["HTTP_REFERER"])

    data_element_grid = DataElementGrid(
        instance.dataelement_set.all(),
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_dhis2:data_element_list", kwargs={"instance_id": instance_id}
        ),
    )
    indicator_grid = IndicatorGrid(
        instance.indicator_set.all(),
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_dhis2:indicator_list", kwargs={"instance_id": instance_id}
        ),
    )

    dataset_grid = DatasetGrid(
        instance.dataset_set.all(),
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_dhis2:dataset_list", kwargs={"instance_id": instance_id}
        ),
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
            "instance_card": instance_card,
            "data_element_grid": data_element_grid,
            "indicator_grid": indicator_grid,
            "dataset_grid": dataset_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_list(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    data_element_grid = DataElementGrid(
        instance.dataelement_set.all(), page=int(request.GET.get("page", "1"))
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
            "data_element_grid": data_element_grid,
            "section_title": _(
                "Data elements in instance %(instance)s"
                % {"instance": instance.display_name}
            ),
            "section_label": "%(start)s to %(end)s out of %(total)s"
            % {
                "start": data_element_grid.start_index,
                "end": data_element_grid.end_index,
                "total": data_element_grid.total_count,
            },
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_detail(request, instance_id, data_element_id):
    instance, data_element = _get_instance_and_data_element(
        request, instance_id, data_element_id
    )
    data_element_card = DataElementCard(data_element, request=request)
    if request.method == "POST" and data_element_card.save():
        return redirect(request.META["HTTP_REFERER"])

    dataset_grid = DatasetGrid(
        data_element.dataset_set.all(), page=int(request.GET.get("page", "1"))
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
            "data_element_card": data_element_card,
            "dataset_grid": dataset_grid,
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

    messages.success(request, _("Added data element to current extract"))

    return redirect(request.META.get("HTTP_REFERER"))


def indicator_list(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    indicator_grid = IndicatorGrid(
        instance.indicator_set.all(), page=int(request.GET.get("page", "1"))
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
            "indicator_grid": indicator_grid,
            "section_title": _(
                "Indicators in instance %(instance)s"
                % {"instance": instance.display_name}
            ),
            "section_label": "%(start)s to %(end)s out of %(total)s"
            % {
                "start": indicator_grid.start_index,
                "end": indicator_grid.end_index,
                "total": indicator_grid.total_count,
            },
            "breadcrumbs": breadcrumbs,
        },
    )


def indicator_detail(request, instance_id, indicator_id):
    instance, indicator = _get_instance_and_indicator(
        request, instance_id, indicator_id
    )
    indicator_card = IndicatorCard(indicator, request=request)
    if request.method == "POST" and indicator_card.save():
        return redirect(request.META["HTTP_REFERER"])

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
            "indicator_card": indicator_card,
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

    messages.success(request, _("Added indicator to current extract"))

    return redirect(request.META.get("HTTP_REFERER"))


def instance_sync(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    sync_result = instance.sync()
    messages.success(request, sync_result)

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

    messages.success(request, _("Delete current extract"))

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


def _get_instance_and_datset(request, instance_id, dataset_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )

    return instance, get_object_or_404(
        DataSet.objects.filter(instance=instance), pk=dataset_id
    )


def _get_instance_and_indicator(request, instance_id, indicator_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )

    return instance, get_object_or_404(
        Indicator.objects.filter(instance=instance), pk=indicator_id
    )


def dataset_list(request, instance_id):
    instance = get_object_or_404(
        Instance.objects.filter_for_user(request.user), pk=instance_id
    )
    dataset_grid = DatasetGrid(
        instance.dataset_set.all(), page=int(request.GET.get("page", "1"))
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
        (_("Data Sets"),),
    ]

    return render(
        request,
        "connector_dhis2/dataset_list.html",
        {
            "instance": instance,
            "dataset_grid": dataset_grid,
            "section_title": _(
                "Data sets in instance %(instance)s"
                % {"instance": instance.display_name}
            ),
            "section_label": "%(start)s to %(end)s out of %(total)s"
            % {
                "start": dataset_grid.start_index,
                "end": dataset_grid.end_index,
                "total": dataset_grid.total_count,
            },
            "breadcrumbs": breadcrumbs,
        },
    )


def dataset_detail(request, instance_id, dataset_id):
    instance, dataset = _get_instance_and_datset(request, instance_id, dataset_id)
    dataset_card = DatasetCard(dataset, request=request)
    if request.method == "POST" and dataset_card.save():
        return redirect(request.META["HTTP_REFERER"])

    data_elements_grid = DataElementGrid(
        dataset.data_elements.all(), page=int(request.GET.get("page", "1"))
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
        (_("Data Sets"), "connector_dhis2:dataset_list", instance_id),
        (dataset.display_name,),
    ]

    return render(
        request,
        "connector_dhis2/dataset_detail.html",
        {
            "instance": instance,
            "dataset": dataset,
            "dataset_card": dataset_card,
            "data_elements_grid": data_elements_grid,
            "breadcrumbs": breadcrumbs,
        },
    )
