"""Fallback export when psql is not at hand: run inside the app container.

    python manage.py shell < export_scheduled_pipelines_django.py > scheduled_pipelines.csv

Single values() query, same filters as the scheduler. Nothing is written to the database.
"""

import csv
import sys

from hexa.pipelines.models import Pipeline

rows = (
    Pipeline.objects.exclude(schedule=None)
    .exclude(schedule="")
    .filter(workspace__archived=False)
    .order_by("workspace__slug", "code")
    .values_list(
        "id", "workspace__slug", "code", "name", "schedule", "cpu_request", "memory_request"
    )
    .iterator(chunk_size=500)
)

writer = csv.writer(sys.stdout)
writer.writerow(["id", "workspace", "code", "name", "schedule", "cpu_request", "memory_request"])
for row in rows:
    writer.writerow(row)
