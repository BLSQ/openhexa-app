from django.db import migrations

# Each new tool goes to the connections already granted the tool exposing the same
# data, so no connection reaches anything it could not before: glob_files shows
# paths, as list_files does; grep_files shows contents, as read_file does.
GRANTED_WITH = {
    "glob_files": "list_files",
    "grep_files": "read_file",
}


def grant_file_search_tools(apps, schema_editor):
    MCPConnection = apps.get_model("mcp", "MCPConnection")
    connections = []
    for connection in MCPConnection.objects.all():
        granted = set(connection.tools)
        added = {new for new, existing in GRANTED_WITH.items() if existing in granted}
        if added - granted:
            connection.tools = sorted(granted | added)
            connections.append(connection)
    MCPConnection.objects.bulk_update(connections, ["tools"])


def revoke_file_search_tools(apps, schema_editor):
    MCPConnection = apps.get_model("mcp", "MCPConnection")
    connections = []
    for connection in MCPConnection.objects.all():
        kept = [tool for tool in connection.tools if tool not in GRANTED_WITH]
        if kept != connection.tools:
            connection.tools = kept
            connections.append(connection)
    MCPConnection.objects.bulk_update(connections, ["tools"])


class Migration(migrations.Migration):
    dependencies = [
        ("mcp", "0002_mcp_connection"),
    ]

    operations = [
        migrations.RunPython(grant_file_search_tools, revoke_file_search_tools),
    ]
