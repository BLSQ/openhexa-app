from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0065_workspacetokenusage"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="public_files_enabled",
            field=models.BooleanField(default=False),
        ),
    ]
