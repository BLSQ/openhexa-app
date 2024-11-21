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
        ),
        migrations.AddIndex(
            model_name="pipelineversion",
            index=models.Index(fields=["pipeline", "version_number"]),
        ),
        migrations.AlterField(
            model_name="pipelineversion",
            name="name",
            field=models.CharField(max_length=250, null=False, blank=False),
        ),
    ]
