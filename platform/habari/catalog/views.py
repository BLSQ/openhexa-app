from datetime import timedelta

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404

from .models import DataSource

SAMPLE_DATASOURCES = [
    {
        "id": "aecc5e5e-d323-4398-9b86-5871afdd500f",
        "type": {"code": "dhis2", "label": "DHIS2", "description": "DHIS2 instance"},
        "name": "DHIS 2 Demo",
        "owner": {
            "name": "HISP",
            "website": "https://www.mn.uio.no/ifi/english/research/networks/hisp/",
            "type": {"code": "academia", "label": "Academic"},
        },
        "contact": {"name": "Support mail", "email": "post@dhis2.org", },
        "url": "https://play.dhis2.org/2.35.0/",
        "location": {"icon": "🇸🇱", "name": "Sierra Leone", "iso3": "SLE"},
        "content": {
            "quantity": "83 data elements",
            "tags": [{"code": "public", "label": "Public", "color": "green"}],
        },
        "data_elements": [
            {
                "id": "434169d5-d94c-47e1-a1b1-7a1b6b61133c",
                "code": "DE_359596",
                "name": "ANC 1st visit",
                "short_name": "ANC 1st visit",
                "description": "",
                "domain_type": {"code": "aggregate", "label": "Aggregate", },
                "value_type": {"code": "number", "label": "Number"},
                "aggregation_type": {"code": "sum", "label": "Sum", },
                "tags": [
                    {"code": "malaria", "label": "Malaria", "color": "green"},
                    {"code": "care_cases", "label": "Care cases", "color": "yellow"},
                ],
            },
            {
                "id": "739ff5fe-59fe-4e63-a17e-69d6852f7a37",
                "code": "DE_359597",
                "name": "ANC 2nd visit",
                "short_name": "ANC 2nd visit",
                "description": "",
                "domain_type": {"code": "aggregate", "label": "Aggregate", },
                "value_type": {"code": "number", "label": "Number"},
                "aggregation_type": {"code": "sum", "label": "Sum", },
                "tags": [
                    {"code": "malaria", "label": "Malaria", "color": "green"},
                    {"code": "care_cases", "label": "Care cases", "color": "yellow"},
                ],
            },
            {
                "id": "03ee9f97-391e-4044-b26e-ead4bb1a0224",
                "code": "DE_359598",
                "name": "ANC 3rd visit",
                "short_name": "ANC 3rd visit",
                "description": "",
                "domain_type": {"code": "aggregate", "label": "Aggregate", },
                "value_type": {"code": "number", "label": "Number"},
                "aggregation_type": {"code": "sum", "label": "Sum", },
                "tags": [
                    {"code": "malaria", "label": "Malaria", "color": "green"},
                    {"code": "care_cases", "label": "Care cases", "color": "yellow"},
                ],
            },
            {
                "id": "cc1e3d45-7975-4d4b-8e5b-5512a2271f21",
                "code": "DE_359599",
                "name": "ANC 4th or more visit",
                "short_name": "ANC 4th or more",
                "description": "",
                "domain_type": {"code": "aggregate", "label": "Aggregate", },
                "value_type": {"code": "number", "label": "Number"},
                "aggregation_type": {"code": "sum", "label": "Sum", },
                "tags": [
                    {"code": "malaria", "label": "Malaria", "color": "green"},
                    {"code": "care_cases", "label": "Care cases", "color": "yellow"},
                ],
            },
            {
                "id": "56a32844-4ccf-45e1-9348-ab218c031368",
                "code": "DE_3000005",
                "name": "Admission Date",
                "short_name": "Admission Date",
                "description": "Date of Admission of patient.",
                "domain_type": {"code": "tracker", "label": "Tracker", },
                "value_type": {"code": "date", "label": "Date"},
                "aggregation_type": {"code": "average", "label": "Average", },
                "tags": [
                    {"code": "malaria", "label": "Malaria", "color": "green"},
                    {"code": "care_cases", "label": "Testing", "color": "yellow"},
                ],
            },
            {
                "id": "3b2ed9c3-5e2d-4ad7-a2c2-1caeab8d1202",
                "code": "DE_3000003",
                "name": "Age in years",
                "short_name": "Age in years",
                "description": "Age of person in years.",
                "domain_type": {"code": "tracker", "label": "Tracker", },
                "value_type": {"code": "integer", "label": "Integer"},
                "aggregation_type": {"code": "average", "label": "Average", },
            },
        ],
        "last_updated_on": timezone.now() - timedelta(days=1),
        "update_frequency": {"code": "daily", "label": "Updated daily"},
    },
    {
        "id": "831cfa1b-f8ec-474b-a3c9-da8ca58684be",
        "type": {"code": "dhis2", "label": "DHIS2", "description": "DHIS2 instance"},
        "name": "Another dhis2 instance",
        "owner": {
            "name": "Ministry of Health",
            "website": "https://www.minisanterdc.cd/",
            "type": {"code": "government", "label": "Government"},
        },
        "location": {
            "icon": "🇨🇩",
            "name": "Democratic Republic of the Congo",
            "iso3": "COD",
        },
        "content": {
            "quantity": "32 data elements",
            "tags": [{"code": "pii", "label": "Contains PII", "color": "red"}],
        },
        "last_updated_on": timezone.now() - timedelta(days=3),
        "update_frequency": {"code": "weekly", "label": "Updated weekly"},
    },
    {
        "id": "b4de249d-449a-4a9c-a39b-ea2e83bd8dc5",
        "type": {"code": "iaso", "label": "IASO HFR", "description": "IASO project"},
        "name": "Carte Sanitaire DRC",
        "owner": {
            "name": "Ministry of Health",
            "website": "https://www.minisanterdc.cd/",
            "type": {"code": "government", "label": "Government"},
        },
        "location": {
            "icon": "🇨🇩",
            "name": "Democratic Republic of the Congo",
            "iso3": "COD",
        },
        "content": {"quantity": "7 pyramids", "tags": [], },
        "last_updated_on": timezone.now() - timedelta(days=1),
        "update_frequency": {"code": "daily", "label": "Updated daily"},
    },
    {
        "id": "dcac5818-0f1a-4f52-98f2-4d514b7d7725",
        "type": {
            "code": "excel",
            "label": "Excel file",
            "description": "Microsoft Excel file",
        },
        "name": "COVID Linelist",
        "owner": {
            "name": "Ministry of Health",
            "website": "https://www.minisanterdc.cd/",
            "type": {"code": "government", "label": "Government"},
        },
        "location": {
            "icon": "🇨🇩",
            "name": "Democratic Republic of the Congo",
            "iso3": "COD",
        },
        "content": {
            "quantity": "1 file",
            "tags": [{"code": "pii", "label": "Contains PII", "color": "red"}],
        },
        "last_updated_on": timezone.now() - timedelta(days=15),
        "update_frequency": {"code": "adhoc", "label": "Ad-hoc updates"},
    },
    {
        "id": "14934a3d-e6c1-40c1-85a7-be099e5f7689",
        "type": {
            "code": "csv",
            "label": "CSV file",
            "description": "Comma-separated values file",
        },
        "name": "Worldpop Birth data",
        "owner": {
            "name": "Worldpop",
            "website": "https://www.worldpop.org/",
            "type": {"code": "academia", "label": "Academia"},
        },
        "location": {"icon": "🌏", "name": "Global", "iso3": None},
        "content": {
            "quantity": "13 files",
            "tags": [{"code": "public", "label": "Public", "color": "green"}],
        },
        "last_updated_on": timezone.now() - timedelta(days=44),
        "update_frequency": {"code": "adhoc", "label": "Ad-hoc updates"},
    },
]


def index(request):
    breadcrumbs = [("Catalog", "catalog:index")]
    datasources = DataSource.objects.all()

    return render(
        request,
        "catalog/index.html",
        {"datasources": datasources, "breadcrumbs": breadcrumbs},
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


def datasource_refresh(request, datasource_id):
    datasource = get_object_or_404(DataSource, pk=datasource_id)
    refresh_message = datasource.refresh()
    messages.success(request, refresh_message)

    return HttpResponseRedirect(reverse('catalog:index'))
