from django.db import migrations


def nothing(*args, **kwargs):
    pass


def migrate_parameters_and_entrypoint(apps, schema_editor):
    PipelineVersion = apps.get_model("pipelines", "PipelineVersion")

    for pv in PipelineVersion.objects.all():
        p = pv.pipeline
        pv.entrypoint = p.entrypoint
        pv.parameters = p.parameters
        pv.save()


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0014_remove_pipeline_user_pipeline_workspace_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_parameters_and_entrypoint, nothing),
    ]
