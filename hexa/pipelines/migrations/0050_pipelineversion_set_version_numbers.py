from django.db import migrations


def set_version_numbers(apps, _):
    PipelineVersion = apps.get_model("pipelines", "PipelineVersion")
    pipelines = PipelineVersion.objects.values_list("pipeline", flat=True).distinct()

    for pipeline in pipelines:
        versions = PipelineVersion.objects.filter(pipeline=pipeline).order_by(
            "created_at"
        )
        for version_number, version in enumerate(versions, start=1):
            version.version_number = version_number
            version.save(update_fields=["version_number"])


def revert_version_numbers(apps, _):
    PipelineVersion = apps.get_model("pipelines", "PipelineVersion")
    PipelineVersion.objects.update(version_number=1)


class Migration(migrations.Migration):
    dependencies = [("pipelines", "0049_pipelineversion_version_number")]

    operations = [
        migrations.RunPython(set_version_numbers, reverse_code=revert_version_numbers),
    ]
