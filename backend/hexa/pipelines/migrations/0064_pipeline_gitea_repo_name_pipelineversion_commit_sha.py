from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0063_alter_pipelinerun_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipelineversion",
            name="commit_sha",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="pipeline",
            name="gitea_repo_name",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
