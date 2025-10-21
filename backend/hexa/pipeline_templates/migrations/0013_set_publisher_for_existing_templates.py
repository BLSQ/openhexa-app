from django.db import migrations


def set_publisher_for_existing_templates(apps, schema_editor):
    PipelineTemplate = apps.get_model("pipeline_templates", "PipelineTemplate")

    for template in PipelineTemplate.objects.all():
        if template.publisher:
            continue

        publisher = "Community"
        if template.workspace and template.workspace.organization:
            if template.workspace.organization.name == "Bluesquare":
                publisher = "Bluesquare"

        template.publisher = publisher
        template.save(update_fields=["publisher"])


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline_templates", "0012_pipelinetemplate_publisher"),
    ]

    operations = [
        migrations.RunPython(
            set_publisher_for_existing_templates,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
