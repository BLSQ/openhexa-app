import csv
import typing
from operator import attrgetter

from django.db.models import QuerySet
from django.http import HttpResponse


def _get_or_none(obj: typing.Any, field: str) -> typing.Any:
    try:
        return attrgetter(field)(obj)
    except (AttributeError, KeyError):
        return None


def render_queryset_to_csv(
    queryset: QuerySet, *, filename: str, field_names: typing.Sequence[str]
) -> HttpResponse:
    """Generate a response with csv content for the provided queryset and field names.
    Field names may include a dot for nested field access.
    .
    """
    if not filename.endswith(".csv"):
        return HttpResponse(
            f"Invalid filename {filename} - should end by .csv".encode(),
            status=400,
        )
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )

    writer = csv.writer(response)
    writer.writerow([n.replace(".", "_") for n in field_names])

    for obj in queryset:
        writer.writerow([_get_or_none(obj, field) for field in field_names])

    return response
