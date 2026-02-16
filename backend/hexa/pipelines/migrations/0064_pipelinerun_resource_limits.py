from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0063_alter_pipelinerun_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipelinerun",
            name="cpu_limit",
            field=models.CharField(
                max_length=32, default=settings.PIPELINE_DEFAULT_CONTAINER_CPU_LIMIT
            ),
        ),
        migrations.AddField(
            model_name="pipelinerun",
            name="memory_limit",
            field=models.CharField(
                max_length=32, default=settings.PIPELINE_DEFAULT_CONTAINER_MEMORY_LIMIT
            ),
        ),
    ]
