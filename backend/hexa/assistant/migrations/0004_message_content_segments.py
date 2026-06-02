from django.db import migrations, models


class Migration(migrations.Migration):
    # Splitting ALTER TABLE and UPDATE into separate operations avoids the
    # "pending trigger events" error that occurs when both run in one transaction.
    atomic = False

    dependencies = [
        ("assistant", "0003_conversation_generic_linked_object"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE assistant_message
                  ALTER COLUMN content TYPE jsonb
                  USING jsonb_build_array(jsonb_build_object('type', 'text', 'content', content));
            """,
            reverse_sql="""
                ALTER TABLE assistant_message
                  ALTER COLUMN content TYPE text
                  USING COALESCE(content->0->>'content', '');
            """,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE assistant_message m
                SET content = m.content || (
                    SELECT jsonb_agg(
                        jsonb_build_object('type', 'tool', 'tool_call_id', ti.tool_call_id)
                        ORDER BY ti.created_at
                    )
                    FROM assistant_toolinvocation ti WHERE ti.message_id = m.id
                )
                WHERE EXISTS (
                    SELECT 1 FROM assistant_toolinvocation ti WHERE ti.message_id = m.id
                );
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="message",
                    name="content",
                    field=models.JSONField(),
                ),
            ],
            database_operations=[],
        ),
    ]
