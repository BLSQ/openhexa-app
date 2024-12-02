from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("pipelines", "0050_pipelineversion_set_version_numbers")]

    operations = [
        migrations.AddConstraint(
            model_name="pipelineversion",
            constraint=models.UniqueConstraint(
                fields=("pipeline", "version_number"),
                name="unique_pipeline_version_number",
            ),
        ),
        migrations.AddIndex(
            model_name="pipelineversion",
            index=models.Index(
                fields=["pipeline", "version_number"],
                name="index_pipeline_version_number",
            ),
        ),
        migrations.AlterField(
            model_name="pipelineversion",
            name="name",
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
    ]
