import uuid
from logging import getLogger

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .datacards import FormCard, IASOCard, OrgUnitCard
from .datagrids import FormGrid, OrgUnitGrid
from .models import Account

logger = getLogger(__name__)


def datasource_detail(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    iaso_account = get_object_or_404(
        Account.objects.filter_for_user(request.user),
        pk=datasource_id,
    )

    iaso_card = IASOCard(iaso_account, request=request)
    if request.method == "POST" and iaso_card.save():
        return redirect(request.META["HTTP_REFERER"])

    form_grid = FormGrid(
        iaso_account.form_set.prefetch_indexes().select_related("iaso_account"),
        parent_model=iaso_account,
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_iaso:form_index", kwargs={"datasource_id": datasource_id}
        ),
        request=request,
    )

    orgunit_grid = OrgUnitGrid(
        iaso_account.orgunit_set.prefetch_indexes().select_related("iaso_account"),
        parent_model=iaso_account,
        per_page=5,
        paginate=False,
        more_url=reverse(
            "connector_iaso:orgunit_index", kwargs={"datasource_id": datasource_id}
        ),
        request=request,
    )

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (iaso_account.display_name, "connector_iaso:datasource_detail", datasource_id),
    ]

    return render(
        request,
        "connector_iaso/iaso_index.html",
        {
            "datasource": iaso_account,
            "breadcrumbs": breadcrumbs,
            "iaso_card": iaso_card,
            "form_grid": form_grid,
            "orgunit_grid": orgunit_grid,
        },
    )


def form_index(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    iaso_account = get_object_or_404(
        Account.objects.filter_for_user(request.user),
        pk=datasource_id,
    )

    iaso_card = IASOCard(iaso_account, request=request)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (iaso_account.display_name, "connector_iaso:datasource_detail", datasource_id),
        (_("Forms"), "connector_iaso:form_index", datasource_id),
    ]

    form_grid = FormGrid(
        iaso_account.form_set.prefetch_indexes().select_related("iaso_account"),
        parent_model=iaso_account,
        per_page=20,
        page=int(request.GET.get("page", "1")),
        request=request,
    )

    return render(
        request,
        "connector_iaso/form_index.html",
        {
            "datasource": iaso_account,
            "breadcrumbs": breadcrumbs,
            "iaso_card": iaso_card,
            "form_grid": form_grid,
        },
    )


def form_detail(
    request: HttpRequest, account_id: uuid.UUID, iaso_id: int
) -> HttpResponse:
    iaso_account = get_object_or_404(
        Account.objects.filter_for_user(request.user),
        pk=account_id,
    )
    form_object = get_object_or_404(
        iaso_account.form_set.prefetch_indexes(), iaso_id=iaso_id
    )
    form_card = FormCard(model=form_object, request=request)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (iaso_account.name, "connector_iaso:datasource_detail", account_id),
        (_("Forms"), "connector_iaso:form_index", account_id),
    ]

    return render(
        request,
        "connector_iaso/form_detail.html",
        {
            "datasource": iaso_account,
            "form_object": form_object,
            "form_card": form_card,
            "breadcrumbs": breadcrumbs,
            "default_tab": "details",
        },
    )


def orgunit_index(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    iaso_account = get_object_or_404(
        Account.objects.filter_for_user(request.user),
        pk=datasource_id,
    )

    iaso_card = IASOCard(iaso_account, request=request)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (iaso_account.display_name, "connector_iaso:datasource_detail", datasource_id),
        (_("OrgUnit"), "connector_iaso:orgunit_index", datasource_id),
    ]

    orgunit_grid = OrgUnitGrid(
        iaso_account.orgunit_set.prefetch_indexes().select_related("iaso_account"),
        parent_model=iaso_account,
        per_page=20,
        page=int(request.GET.get("page", "1")),
        request=request,
    )

    return render(
        request,
        "connector_iaso/ou_index.html",
        {
            "datasource": iaso_account,
            "breadcrumbs": breadcrumbs,
            "iaso_card": iaso_card,
            "ou_grid": orgunit_grid,
        },
    )


def orgunit_detail(
    request: HttpRequest, account_id: uuid.UUID, iaso_id: int
) -> HttpResponse:
    iaso_account = get_object_or_404(
        Account.objects.filter_for_user(request.user),
        pk=account_id,
    )
    orgunit_object = get_object_or_404(
        iaso_account.orgunit_set.prefetch_indexes(), iaso_id=iaso_id
    )
    orgunit_card = OrgUnitCard(model=orgunit_object, request=request)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (iaso_account.name, "connector_iaso:datasource_detail", account_id),
        (_("OrgUnit"), "connector_iaso:orgunit_index", account_id),
    ]

    return render(
        request,
        "connector_iaso/ou_detail.html",
        {
            "datasource": iaso_account,
            "orgunit_object": orgunit_object,
            "orgunit_card": orgunit_card,
            "breadcrumbs": breadcrumbs,
            "default_tab": "details",
        },
    )
