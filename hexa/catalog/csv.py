import csv
import typing

from django.db.models import QuerySet
from django.http import HttpResponse


def write_queryset_to_csv(
    queryset: QuerySet,
    *,
    target: typing.Union[typing.IO, HttpResponse],
    field_names: typing.Sequence[str]
):
    """Take a writable object and write CSV depending on queryset and field_names"""

    writer = csv.writer(target)
    writer.writerow(field_names)

    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
