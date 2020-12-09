from datetime import timedelta
from math import floor

from django.utils import timezone
from django.shortcuts import render

SAMPLE_DATASOURCES = [
    {
        "id": "aecc5e5e-d323-4398-9b86-5871afdd500f",
        "type": {"code": "dhis2", "label": "DHIS2",},
        "name": "A dhis2 instance",
        "source": {
            "name": "A ministry of health somewhere",
            "type": {"code": "government", "label": "Government"},
        },
        "datasets_count": 3,
        "tags": [{"code": "pii", "label": "Contains PII", "color": "red"}],
        "last_updated_on": timezone.now() - timedelta(days=1),
        "update_frequency": {"code": "daily", "label": "Updated daily"},
    },
    {
        "id": "831cfa1b-f8ec-474b-a3c9-da8ca58684be",
        "type": {"code": "dhis2", "label": "DHIS2",},
        "name": "Another dhis2 instance",
        "source": {"name": "A partner NGO", "type": {"code": "ngo", "label": "NGO"}},
        "datasets_count": 2,
        "tags": [{"code": "public", "label": "Public", "color": "green"}],
        "last_updated_on": timezone.now() - timedelta(days=3),
        "update_frequency": {"code": "weekly", "label": "Updated weekly"},
    },
    {
        "id": "b4de249d-449a-4a9c-a39b-ea2e83bd8dc5",
        "type": {"code": "iaso", "label": "IASO",},
        "name": "A Iaso project",
        "source": {
            "name": "SNIS something",
            "type": {"code": "government", "label": "Government"},
        },
        "datasets_count": 7,
        "tags": [],
        "last_updated_on": timezone.now() - timedelta(days=1),
        "update_frequency": {"code": "daily", "label": "Updated daily"},
    },
    {
        "id": "dcac5818-0f1a-4f52-98f2-4d514b7d7725",
        "type": {"code": "excel", "label": "Excel file",},
        "name": "Running out of ideas here",
        "source": {
            "name": "An academic partner",
            "type": {"code": "academia", "label": "Academia"},
        },
        "datasets_count": 1,
        "tags": [{"code": "pii", "label": "Contains PII", "color": "red"}],
        "last_updated_on": timezone.now() - timedelta(days=15),
        "update_frequency": {"code": "adhoc", "label": "Ad-hoc updates"},
    },
    {
        "id": "14934a3d-e6c1-40c1-85a7-be099e5f7689",
        "type": {"code": "csv", "label": "CSV file",},
        "name": "Seriously, help me",
        "source": {
            "name": "World health organization",
            "type": {"code": "internation", "label": "Internation Institution"},
        },
        "datasets_count": 9,
        "tags": [{"code": "public", "label": "Public", "color": "green"}],
        "last_updated_on": timezone.now() - timedelta(days=44),
        "update_frequency": {"code": "adhoc", "label": "Ad-hoc updates"},
    },
]


def index(request):
    breadcrumbs = [("Catalog", "catalog:index")]

    return render(
        request,
        "catalog/index.html",
        {"datasources": SAMPLE_DATASOURCES, "breadcrumbs": breadcrumbs},
    )


def datasource_detail(request, datasource_id):
    datasource = next(ds for ds in SAMPLE_DATASOURCES if ds["id"] == datasource_id)
    breadcrumbs = [
        ("Catalog", "catalog:index"),
        (datasource["name"], "catalog:detail", datasource_id),
    ]

    return render(
        request,
        "catalog/datasource_detail.html",
        {"datasource": datasource, "breadcrumbs": breadcrumbs},
    )
