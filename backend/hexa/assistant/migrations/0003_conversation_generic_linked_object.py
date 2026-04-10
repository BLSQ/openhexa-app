import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assistant", "0002_conversation_asst_conv_user_cost_idx"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="instruction_set",
            field=models.CharField(
                choices=[
                    ("general", "General"),
                    ("pipeline", "Pipeline"),
                    ("edit_pipeline", "Edit Pipeline"),
                    ("webapps", "Web Apps"),
                ],
                default="general",
                max_length=50,
            ),
        ),
        # Drop the pipeline FK column if it exists (left over from old migration 0003
        # on existing databases that had it applied before this squash)
        migrations.RunSQL(
            "ALTER TABLE assistant_conversation DROP COLUMN IF EXISTS pipeline_id;",
            migrations.RunSQL.noop,
        ),
        migrations.AddField(
            model_name="conversation",
            name="linked_object_content_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="conversation",
            name="linked_object_id",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(
                fields=["linked_object_content_type", "linked_object_id"],
                name="asst_conv_linked_object_idx",
            ),
        ),
    ]
