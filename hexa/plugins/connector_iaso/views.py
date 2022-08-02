import uuid
from logging import getLogger

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .datacards import FormCard, IASOCard
from .datagrids import FormGrid
from .models import IASOAccount

logger = getLogger(__name__)


def datasource_detail(request: HttpRequest, datasource_id: uuid.UUID) -> HttpResponse:
    iaso_account = get_object_or_404(
        IASOAccount.objects.filter_for_user(request.user),
        pk=datasource_id,
    )

    iaso_card = IASOCard(iaso_account, request=request)
    if request.method == "POST" and iaso_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (iaso_account.display_name, "connector_iaso:datasource_detail", datasource_id),
    ]

    form_grid = FormGrid(
        iaso_account.iasoform_set.prefetch_indexes().select_related("iaso_account"),
        parent_model=iaso_account,
        prefix="",
        per_page=20,
        page=int(request.GET.get("page", "1")),
        request=request,
    )

    return render(
        request,
        "connector_iaso/iaso_index.html",
        {
            "datasource": iaso_account,
            "breadcrumbs": breadcrumbs,
            "iaso_card": iaso_card,
            "form_grid": form_grid,
        },
    )


def form_detail(
    request: HttpRequest, iasoaccount_id: uuid.UUID, iaso_id: int
) -> HttpResponse:
    iaso_account = get_object_or_404(
        IASOAccount.objects.filter_for_user(request.user),
        pk=iasoaccount_id,
    )
    form_object = get_object_or_404(
        iaso_account.iasoform_set.prefetch_indexes(), iaso_id=iaso_id
    )
    form_card = FormCard(model=form_object, request=request)

    breadcrumbs = [
        (_("Catalog"), "catalog:index"),
        (iaso_account.name, "connector_iaso:datasource_detail", iasoaccount_id),
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
