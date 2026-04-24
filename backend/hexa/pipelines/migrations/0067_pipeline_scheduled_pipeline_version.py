import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0066_pipelinerun_state_execution_date_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipeline",
            name="scheduled_pipeline_version",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="scheduled_for_pipelines",
                to="pipelines.pipelineversion",
            ),
        ),
    ]
