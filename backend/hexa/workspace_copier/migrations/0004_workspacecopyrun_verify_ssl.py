from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workspace_copier", "0003_workspacecopyrun_same_server"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspacecopyrun",
            name="verify_ssl",
            field=models.BooleanField(default=True),
        ),
    ]
