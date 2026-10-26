from django.db import migrations

# One row per assistant message that recorded usage, so the limits and the
# admin keep their history now that they read AiUsage. Which model ran is not
# known for these rows, hence the empty provider and model name. The naming
# agent's cost was only ever folded into the conversation total and is not
# recoverable per call.
BACKFILL = """
INSERT INTO assistant_aiusage (
    id, created_at, updated_at, organization_id, workspace_id, user_id,
    conversation_id, message_id, source, provider, model_name,
    input_tokens, cache_read_tokens, cache_write_tokens, output_tokens,
    cost, external_id
)
SELECT
    gen_random_uuid(), m.created_at, m.created_at, w.organization_id,
    c.workspace_id, c.user_id, c.id, m.id, 'conversation', '', '',
    GREATEST(COALESCE(m.input_tokens, 0), 0), 0, 0,
    GREATEST(COALESCE(m.output_tokens, 0), 0), m.cost, NULL
FROM assistant_message m
JOIN assistant_conversation c ON c.id = m.conversation_id
JOIN workspaces_workspace w ON w.id = c.workspace_id
WHERE m.role = 'assistant'
  AND (m.input_tokens IS NOT NULL OR m.cost IS NOT NULL)
  AND NOT EXISTS (SELECT 1 FROM assistant_aiusage u WHERE u.message_id = m.id);
"""

REVERSE = """
DELETE FROM assistant_aiusage WHERE source = 'conversation' AND message_id IS NOT NULL;
"""


class Migration(migrations.Migration):
    dependencies = [("assistant", "0008_aiusage")]

    operations = [migrations.RunSQL(BACKFILL, REVERSE)]
