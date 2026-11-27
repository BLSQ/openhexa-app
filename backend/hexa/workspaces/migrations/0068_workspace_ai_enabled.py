from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0067_workspace_public_files_enabled"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="ai_enabled",
            field=models.BooleanField(default=True),
        ),
    ]
