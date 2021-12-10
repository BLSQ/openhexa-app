import uuid

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hexa.catalog.csv import render_queryset_to_csv

from .datacards import (
    DataElementCard,
    DatasetCard,
    IndicatorCard,
    InstanceCard,
    OrganisationUnitCard,
)
from .datagrids import DataElementGrid, DatasetGrid, IndicatorGrid, OrganisationUnitGrid
from .models import DataElement, DataSet, Extract, Indicator, Instance, OrganisationUnit


def instance_detail(request: HttpRequest, instance_id: uuid.UUID) -> HttpResponse:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )
    instance_card = InstanceCard(instance, request=request)
    if request.method == "POST" and instance_card.save():
        return redirect(request.META["HTTP_REFERER"])

    data_element_grid = DataElementGrid(
        instance.dataelement_set.prefetch_indexes(),
        parent_model=instance,
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_dhis2:data_element_list", kwargs={"instance_id": instance_id}
        ),
        request=request,
    )
    indicator_grid = IndicatorGrid(
        instance.indicator_set.prefetch_indexes().select_related("indicator_type"),
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_dhis2:indicator_list", kwargs={"instance_id": instance_id}
        ),
        request=request,
    )
    organisation_unit_grid = OrganisationUnitGrid(
        instance.organisationunit_set.filter(path__depth__in=(0, 1)).prefetch_indexes(),
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_dhis2:organisation_unit_list",
            kwargs={"instance_id": instance_id},
        ),
        request=request,
    )
    dataset_grid = DatasetGrid(
        instance.dataset_set.prefetch_indexes(),
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_dhis2:dataset_list", kwargs={"instance_id": instance_id}
        ),
        request=request,
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
            "organisation_unit_grid": organisation_unit_grid,
            "dataset_grid": dataset_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_list(request: HttpRequest, instance_id: uuid.UUID) -> HttpResponse:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )
    data_element_grid = DataElementGrid(
        instance.dataelement_set.prefetch_indexes(),
        parent_model=instance,
        page=int(request.GET.get("page", "1")),
        request=request,
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


def data_element_download(request: HttpRequest, instance_id: uuid.UUID) -> HttpResponse:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )

    return render_queryset_to_csv(
        instance.dataelement_set.prefetch_indexes(),
        filename=request.GET.get("filename", ""),
        field_names=["id"],
    )


def organisation_unit_list(
    request: HttpRequest, instance_id: uuid.UUID
) -> HttpResponse:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )
    organisation_unit_grid = OrganisationUnitGrid(
        instance.organisationunit_set.order_by(
            "path__depth", "name"
        ).prefetch_indexes(),
        parent_model=instance,
        page=int(request.GET.get("page", "1")),
        request=request,
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
        (_("Organisation Units"),),
    ]

    return render(
        request,
        "connector_dhis2/organisation_unit_list.html",
        {
            "instance": instance,
            "organisation_unit_grid": organisation_unit_grid,
            "section_title": _(
                "Organisation Units in instance %(instance)s"
                % {"instance": instance.display_name}
            ),
            "section_label": "%(start)s to %(end)s out of %(total)s"
            % {
                "start": organisation_unit_grid.start_index,
                "end": organisation_unit_grid.end_index,
                "total": organisation_unit_grid.total_count,
            },
            "breadcrumbs": breadcrumbs,
        },
    )


def data_element_detail(
    request: HttpRequest, instance_id: uuid.UUID, data_element_id: uuid.UUID
) -> HttpResponse:
    instance, data_element = _get_instance_and_data_element(
        request, instance_id, data_element_id
    )
    data_element_card = DataElementCard(data_element, request=request)
    if request.method == "POST" and data_element_card.save():
        return redirect(request.META["HTTP_REFERER"])

    dataset_grid = DatasetGrid(
        data_element.dataset_set.prefetch_indexes(),
        page=int(request.GET.get("page", "1")),
        request=request,
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


def organisation_unit_detail(
    request: HttpRequest, instance_id: uuid.UUID, organisation_unit_id: uuid.UUID
) -> HttpResponse:
    instance, organisation_unit = _get_instance_and_organisation_unit(
        request, instance_id, organisation_unit_id
    )
    organisation_unit_card = OrganisationUnitCard(organisation_unit, request=request)
    if request.method == "POST" and organisation_unit_card.save():
        return redirect(request.META["HTTP_REFERER"])

    dataset_grid = DatasetGrid(
        organisation_unit.datasets.prefetch_indexes(),
        page=int(request.GET.get("ds_page", "1")),
        page_parameter_name="ds_page",
        request=request,
    )

    sub_organisation_unit_grid = OrganisationUnitGrid(
        instance.organisationunit_set.direct_children_of(
            organisation_unit
        ).prefetch_indexes(),
        page=int(request.GET.get("ou_page", "1")),
        page_parameter_name="ou_page",
        request=request,
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (instance.display_name, "connector_dhis2:instance_detail", instance_id),
        (
            _("Organisation Units"),
            "connector_dhis2:organisation_unit_list",
            instance_id,
        ),
    ]

    for ou in instance.organisationunit_set.ancestors_of(organisation_unit).order_by(
        "path__depth"
    ):
        breadcrumbs.append(
            (
                ou.display_name,
                "connector_dhis2:organisation_unit_detail",
                instance_id,
                ou.id,
            )
        )

    return render(
        request,
        "connector_dhis2/organisation_unit_detail.html",
        {
            "instance": instance,
            "organisation_unit": organisation_unit,
            "organisation_unit_card": organisation_unit_card,
            "dataset_grid": dataset_grid,
            "sub_organisation_unit_grid": sub_organisation_unit_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


def indicator_list(request: HttpRequest, instance_id: uuid.UUID) -> HttpResponse:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )
    indicator_grid = IndicatorGrid(
        instance.indicator_set.prefetch_indexes().select_related("indicator_type"),
        page=int(request.GET.get("page", "1")),
        request=request,
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


def indicator_detail(
    request: HttpRequest, instance_id: uuid.UUID, indicator_id: uuid.UUID
) -> HttpResponse:
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


def dataset_list(request: HttpRequest, instance_id: uuid.UUID) -> HttpResponse:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )
    dataset_grid = DatasetGrid(
        instance.dataset_set.prefetch_indexes(),
        page=int(request.GET.get("page", "1")),
        request=request,
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


def dataset_detail(
    request: HttpRequest, instance_id: uuid.UUID, dataset_id: uuid.UUID
) -> HttpResponse:
    instance, dataset = _get_instance_and_dataset(request, instance_id, dataset_id)
    dataset_card = DatasetCard(dataset, request=request)
    if request.method == "POST" and dataset_card.save():
        return redirect(request.META["HTTP_REFERER"])

    data_elements_grid = DataElementGrid(
        dataset.data_elements.prefetch_indexes().select_related("instance"),
        parent_model=instance,
        page=int(request.GET.get("page", "1")),
        request=request,
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


def _get_instance_and_data_element(
    request: HttpRequest, instance_id: uuid.UUID, data_element_id: uuid.UUID
) -> tuple[Instance, DataElement]:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )

    return instance, get_object_or_404(
        DataElement.objects.prefetch_indexes().filter(instance=instance),
        pk=data_element_id,
    )


def _get_instance_and_organisation_unit(
    request: HttpRequest, instance_id: uuid.UUID, organisation_unit_id: uuid.UUID
) -> tuple[Instance, OrganisationUnit]:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )

    return instance, get_object_or_404(
        OrganisationUnit.objects.prefetch_indexes().filter(instance=instance),
        pk=organisation_unit_id,
    )


def _get_instance_and_dataset(
    request: HttpRequest, instance_id: uuid.UUID, dataset_id: uuid.UUID
) -> tuple[Instance, DataSet]:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )

    return instance, get_object_or_404(
        DataSet.objects.prefetch_indexes().filter(instance=instance), pk=dataset_id
    )


def _get_instance_and_indicator(
    request: HttpRequest, instance_id: uuid.UUID, indicator_id: uuid.UUID
) -> tuple[Instance, Indicator]:
    instance = get_object_or_404(
        Instance.objects.prefetch_indexes().filter_for_user(request.user),
        pk=instance_id,
    )

    return instance, get_object_or_404(
        Indicator.objects.prefetch_indexes().filter(instance=instance), pk=indicator_id
    )


def data_element_extract(
    request: HttpRequest, instance_id: uuid.UUID, data_element_id: uuid.UUID
) -> HttpResponse:  # TODO: should be post + DRY indicators
    instance, data_element = _get_instance_and_data_element(
        request, instance_id, data_element_id
    )

    current_extract = _get_current_extract(request)
    current_extract.data_elements.add(data_element)
    current_extract.save()

    messages.success(request, _("Added data element to current extract"))

    return redirect(request.META.get("HTTP_REFERER"))


def indicator_extract(
    request: HttpRequest, instance_id: uuid.UUID, indicator_id: uuid.UUID
) -> HttpResponse:  # TODO: should be post + DRY data elements
    instance, indicator = _get_instance_and_indicator(
        request, instance_id, indicator_id
    )

    current_extract = _get_current_extract(request)
    current_extract.indicators.add(indicator)
    current_extract.save()

    messages.success(request, _("Added indicator to current extract"))

    return redirect(request.META.get("HTTP_REFERER"))


def extract_detail(request: HttpRequest, extract_id: uuid.UUID) -> HttpResponse:
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


def extract_delete(request: HttpRequest, extract_id: uuid.UUID) -> HttpResponse:
    extract = get_object_or_404(
        Extract.objects.filter_for_user(request.user), id=extract_id
    )
    extract.delete()

    messages.success(request, _("Delete current extract"))

    return redirect(reverse("catalog:index"))


def _get_current_extract(request: HttpRequest) -> Extract:
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
