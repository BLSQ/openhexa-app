import csv
import typing

from django.db.models import QuerySet
from django.http import HttpResponse


def render_queryset_to_csv(
    queryset: QuerySet, *, filename: str, field_names: typing.Sequence[str]
) -> HttpResponse:
    if not filename.endswith(".csv"):
        return HttpResponse(
            f"Invalid filename {filename} - should end by .csv".encode("utf-8"),
            status=400,
        )
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )

    writer = csv.writer(response)
    writer.writerow(field_names)

    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response
