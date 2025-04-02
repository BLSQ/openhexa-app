from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0047_pipelineversion_rename_duplicate_pipeline_version_name")
    ]

    operations = [
        migrations.AddConstraint(
            model_name="pipelineversion",
            constraint=models.UniqueConstraint(
                fields=("pipeline", "name"), name="unique_pipeline_version_name"
            ),
        )
    ]
