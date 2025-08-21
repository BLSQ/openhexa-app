# Generated migration for auto-update pipelines from template feature

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0051_workspace_configuration"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="auto_update_pipelines_from_template",
            field=models.BooleanField(
                default=False,
                help_text="Automatically update pipelines when their source template is updated",
            ),
        ),
    ]
