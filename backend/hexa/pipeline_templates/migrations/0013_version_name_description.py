from django.db import migrations, models


def copy_template_descriptions_to_versions(apps, schema_editor):
    PipelineTemplate = apps.get_model("pipeline_templates", "PipelineTemplate")
    for template in PipelineTemplate.objects.all():
        last_version = template.versions.order_by("created_at").last()
        if last_version and not last_version.description and template.description:
            last_version.description = template.description
            last_version.save(update_fields=["description"])


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline_templates", "0012_pipelinetemplate_validated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipelinetemplateversion",
            name="name",
            field=models.CharField(blank=True, max_length=200, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pipelinetemplateversion",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(
            copy_template_descriptions_to_versions,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="pipelinetemplate",
            name="description",
        ),
    ]
