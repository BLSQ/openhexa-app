from datetime import timedelta
from math import floor

from django.utils import timezone
from django.shortcuts import render

SAMPLE_DATASOURCES = [
    {
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
        "type": {"code": "dhis2", "label": "DHIS2",},
        "name": "Another dhis2 instance",
        "source": {"name": "A partner NGO", "type": {"code": "ngo", "label": "NGO"}},
        "datasets_count": 2,
        "tags": [{"code": "public", "label": "Public", "color": "green"}],
        "last_updated_on": timezone.now() - timedelta(days=3),
        "update_frequency": {"code": "weekly", "label": "Updated weekly"},
    },
    {
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
    return render(request, "catalog/index.html", {"datasources": SAMPLE_DATASOURCES})
