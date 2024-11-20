import logging

from django.db import migrations, models

logger = logging.getLogger(__name__)


def add_timestamp_to_duplicates(apps, schema_editor):
    PipelineVersion = apps.get_model("pipelines", "PipelineVersion")
    duplicates = (
        PipelineVersion.objects.values("pipeline", "name")
        .annotate(count=models.Count("id"))
        .filter(count__gt=1)
    )

    for duplicate in duplicates:
        versions = PipelineVersion.objects.filter(
            pipeline=duplicate["pipeline"], name__contains=duplicate["name"]
        ).order_by("created_at")

        for index, version in enumerate(
            list(versions)[:-1]
        ):  # Skip the most recent version, keep it unchanged
            old_name = version.name
            version.name = f"{old_name} (v{index+1})"
            version.save()
            logger.info(
                f"Updated version name from {old_name} to {version.name} for {version.pipeline}"
            )


class Migration(migrations.Migration):
    dependencies = [("pipelines", "0046_pipelinerecipient_notification_level_and_more")]

    operations = [
        migrations.RunPython(
            add_timestamp_to_duplicates, reverse_code=migrations.RunPython.noop
        )
    ]
