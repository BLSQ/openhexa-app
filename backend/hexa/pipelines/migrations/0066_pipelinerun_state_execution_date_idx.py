from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    # CONCURRENTLY cannot run inside a transaction, so we disable the
    # implicit transaction that Django wraps around each migration.
    atomic = False

    dependencies = [
        ("pipelines", "0065_pipeline_idx_pipeline_name"),
    ]

    operations = [
        AddIndexConcurrently(
            model_name="pipelinerun",
            index=models.Index(fields=["state"], name="idx_pipelinerun_state"),
        ),
        AddIndexConcurrently(
            model_name="pipelinerun",
            index=models.Index(
                fields=["execution_date"], name="idx_pipelinerun_execution_date"
            ),
        ),
    ]
