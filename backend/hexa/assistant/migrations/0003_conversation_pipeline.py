import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assistant", "0002_conversation_asst_conv_user_cost_idx"),
        ("pipelines", "0066_pipelinerun_state_execution_date_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="pipeline",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assistant_conversations",
                to="pipelines.pipeline",
            ),
        ),
    ]
