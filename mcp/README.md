# OpenHEXA MCP Server

Model Context Protocol (MCP) server for OpenHEXA, allowing Claude to interact with your OpenHEXA instance.

## Features

- List and explore workspaces, datasets, pipelines
- Search across OpenHEXA resources
- View dataset versions and files
- Preview dataset file contents
- List connections and webapps
- Get pipeline run information

## Setup

### 1. Install Dependencies

```bash
cd mcp
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `HEXA_SERVER_URL`: Your OpenHEXA instance URL (e.g., `http://localhost:8001`)
- `HEXA_TOKEN`: Your OpenHEXA API token

### 3. Generate OpenHEXA Token

1. Start your local OpenHEXA instance:
   ```bash
   cd /home/jhubinon/Code-Dev/openhexa-app
   docker compose up
   ```

2. Log in to OpenHEXA at http://localhost:8001
3. Go to your user settings or run this command to create a token:
   ```bash
   docker compose run app shell
   # In the Django shell:
   from hexa.user_management.models import User
   from hexa.workspaces.models import WorkspaceToken
   user = User.objects.get(email='root@openhexa.org')
   # Create a workspace token or use the API token endpoint
   ```

### 4. Configure Claude Desktop

For **Claude Desktop App**, add this to your MCP settings configuration:

**On Linux**: `~/.config/Claude/claude_desktop_config.json`
**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openhexa": {
      "command": "python",
      "args": ["/home/jhubinon/Code-Dev/openhexa-app/mcp/openhexa_mcp_server.py"],
      "env": {
        "HEXA_SERVER_URL": "http://localhost:8001",
        "HEXA_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 5. Configure for Claude CLI (this tool)

For **Claude Code CLI**, add this to your MCP settings:

**Location**: `~/.config/claude-code/settings.json`

```json
{
  "mcpServers": {
    "openhexa": {
      "command": "python",
      "args": ["/home/jhubinon/Code-Dev/openhexa-app/mcp/openhexa_mcp_server.py"],
      "env": {
        "HEXA_SERVER_URL": "http://localhost:8001",
        "HEXA_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 6. Test the Server

Restart Claude Desktop or Claude CLI, then try using one of the tools:

```
List my OpenHEXA workspaces
```

## Available Tools

### Workspace & Organization
- `list_workspaces` - List all available workspaces
- `get_workspace_details` - Get details for a specific workspace
- `list_workspace_members` - List members of a workspace
- `list_connections` - List connections in a workspace
- `list_webapps` - List webapps in a workspace

### Datasets
- `list_datasets` - List datasets with pagination
- `get_dataset_details` - Get details for a specific dataset
- `list_dataset_versions` - List all versions of a dataset
- `get_dataset_version_details` - Get detailed information about a dataset version
- `list_dataset_files` - List all files for all versions of a dataset
- `get_dataset_file_details` - Get details for a specific dataset file
- `search_datasets` - Search datasets by name or description
- `list_datasets_by_creator` - List datasets created by a specific user
- `preview_dataset_file` - Preview a dataset file sample

### Pipelines
- `list_pipelines` - List pipelines in a workspace
- `get_pipeline_details` - Get details for a specific pipeline
- `get_pipeline_runs` - Get runs for a specific pipeline
- **`create_pipeline`** - **NEW!** Create a new pipeline with code in a workspace

### Search
- `search_resources` - Search across OpenHEXA resources

## Troubleshooting

### "OpenHEXA SDK not available"

Make sure you've installed the OpenHEXA SDK:
```bash
pip install openhexa-sdk-python
```

### Connection Errors

- Verify your OpenHEXA instance is running: `docker compose ps`
- Check the URL is correct: `http://localhost:8001` (not 8000)
- Ensure your token is valid and has the necessary permissions

### Token Generation

If you need to create a token programmatically:

```bash
cd /home/jhubinon/Code-Dev/openhexa-app
docker compose run app shell -c "
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembership
user = User.objects.get(email='root@openhexa.org')
# Use the user's API token or create a workspace-specific token
print(f'User ID: {user.id}')
"
```

## Development

To run the server directly for testing:

```bash
cd mcp
python openhexa_mcp_server.py
```

The server will start and listen for MCP requests via stdio.
