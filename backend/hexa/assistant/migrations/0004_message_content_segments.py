from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assistant", "0003_conversation_generic_linked_object"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE assistant_message
                  ALTER COLUMN content TYPE jsonb
                  USING (
                    jsonb_build_array(jsonb_build_object('type', 'text', 'content', content))
                    ||
                    COALESCE(
                      (SELECT jsonb_agg(
                          jsonb_build_object('type', 'tool', 'tool_call_id', ti.tool_call_id)
                          ORDER BY ti.created_at
                        )
                        FROM assistant_toolinvocation ti WHERE ti.message_id = id
                      ),
                      '[]'::jsonb
                    )
                  );
            """,
            reverse_sql="""
                ALTER TABLE assistant_message
                  ALTER COLUMN content TYPE text
                  USING (COALESCE((
                    SELECT elem->>'content'
                    FROM jsonb_array_elements(content) AS elem
                    WHERE elem->>'type' = 'text'
                    LIMIT 1
                  ), ''));
            """,
        ),
        migrations.AlterField(
            model_name="message",
            name="content",
            field=models.JSONField(),
        ),
    ]
