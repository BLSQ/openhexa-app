from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("pipelines", "0048_pipelineversion_unique_pipeline_version_name")]

    operations = [
        migrations.AddField(
            model_name="pipelineversion",
            name="version_number",
            field=models.PositiveIntegerField(
                default=1, editable=False
            ),  # Setting dummy default, will be updated in the next migration
            preserve_default=False,
        )
    ]
