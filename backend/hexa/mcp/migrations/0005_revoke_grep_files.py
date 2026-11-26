from django.db import migrations

REMOVED_TOOL = "grep_files"


def revoke_grep_files(apps, schema_editor):
    MCPConnection = apps.get_model("mcp", "MCPConnection")
    connections = []
    for connection in MCPConnection.objects.all():
        if REMOVED_TOOL in connection.tools:
            connection.tools = [t for t in connection.tools if t != REMOVED_TOOL]
            connections.append(connection)
    MCPConnection.objects.bulk_update(connections, ["tools"])


class Migration(migrations.Migration):
    dependencies = [
        ("mcp", "0004_merge_20261102_0925"),
    ]

    operations = [
        # Not reversed: the tool no longer exists, so there is nothing to grant back.
        migrations.RunPython(revoke_grep_files, migrations.RunPython.noop),
    ]
