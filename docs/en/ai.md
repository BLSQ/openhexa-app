<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>AI in OpenHEXA</h1>
</div>
</div>

OpenHEXA uses large language models (LLMs) in two places: the **built-in assistant**, which helps you create and edit pipelines, web apps and SQL queries from inside the app, and the **MCP server**, which lets an AI client of your choice (Claude, ChatGPT, Gemini CLI...) work with your workspaces. This page explains what each one does, what it can access and which models are involved.

!!! warning "AI can make mistakes"
    Generated code, queries and answers can be wrong, incomplete or outdated. Always review what the AI proposes before you accept, run or share it.

## How AI is used

### The built-in assistant

The assistant is available in the workspaces of an organization where an administrator has enabled it (**Organization settings → AI Assistant**). It appears in a few specific places, each with its own narrowly scoped task:

| Where | What it does |
| --- | --- |
| **Pipelines → Create → Create with AI** | Turns your description into a new pipeline with a first version of its code. |
| **Pipeline code editor → chat panel** | Reads the pipeline's files and proposes a new version. Nothing is saved until you review and accept the proposal. |
| **Web Apps → Create → Create with AI** | Creates a static web app from your description, then opens it in the code editor. |
| **Web app code editor → chat panel** | Reads the web app's files and proposes a new version, which you review and accept. |
| **Data Studio → Generate SQL** | Translates a question into a single read-only `SELECT` query. The model only sees the structure of the database (table and column names and types), never the data in the tables. Before it is shown, the query is only planned by the database to catch mistakes, not run. It runs only when you execute it. |

A small model also gives each conversation a short title.

The assistant runs with a fixed set of instructions for each task and declines requests unrelated to OpenHEXA. It cannot run pipelines, execute SQL of its own, change permissions or act outside the workspace of the conversation.

Each user has a monthly usage budget set by the instance. When it is reached, the assistant pauses until the next month.

### The MCP server

OpenHEXA exposes a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server so that external AI assistants can list, read and act on your workspaces. Setup instructions for the supported clients are at `/mcp/wiki` on your OpenHEXA instance (for example <https://app.openhexa.org/mcp/wiki>), and the full tool catalogue at `/mcp`.

Connecting a client works through OAuth: the client sends you to OpenHEXA, where you sign in and choose which workspaces it may access and which tools it may call. You can tighten or revoke these grants at any time from **Account → MCP connections**. Changes apply to the next call.

With MCP, the model is the one of your AI client, not OpenHEXA's. Whatever a tool returns (file contents, dataset previews, pipeline code...) is sent to that client and processed by its provider under their terms, so grant only the workspaces and tools you actually need.

## What the AI can access

In both cases the AI acts **as you**: every tool call goes through the same permission checks as the OpenHEXA interface, so the AI can never see or do more than your own account can. An MCP connection is further limited to the workspaces and tools you granted it.

### Built-in assistant

| Task | Reads | Writes |
| --- | --- | --- |
| Create / edit pipeline | Workspace metadata and description, datasets and dataset file previews, workspace files, connection names and field names (never secret values), the pipeline's own code and files, the OpenHEXA documentation | Creates the pipeline (create); proposes a new version for you to accept (edit) |
| Create / edit web app | Same as pipelines, plus the database schema (tables and columns, not rows), saved queries, the list of pipelines and the web app's files | Creates the web app; creates or updates saved queries; proposes a new version for you to accept |
| Generate SQL | Only the database schema: table and column names and types. It never reads the rows of any table, and no query result is ever sent to the model | Nothing: the query is only shown to you |

If the workspace has a description, it is given to the assistant as context. Workspace administrators can use it to document data conventions, but the assistant treats it as information, not as instructions.

### MCP server

Tools are grouped by resource. Each grant covers one group, with read and write tools granted separately:

| Resource | Read tools | Write tools |
| --- | --- | --- |
| Workspaces | list, get | update |
| Files | list, read | write |
| Datasets | list, get, preview files | create datasets and versions |
| Pipelines | list, get, get run | run, update, create, create version |
| Pipeline templates | list, get | create a pipeline from a template |
| Web apps | list, get, read files | create, update, edit files |
| Databases | schema of tables and columns (not rows) | — |
| Saved queries | list, get SQL | create, update |
| Connections | list names, types and field names (not secret values) | — |

Only the help tool, which returns the OpenHEXA documentation, works without a grant. No MCP tool runs SQL against a workspace database or returns connection secrets.

## Models

!!! info "This will change over time"
    Models evolve quickly. The ones below are in use at the time of writing; OpenHEXA updates them as better or cheaper models become available, without changing how the assistant works. Check the [release notes](https://github.com/BLSQ/openhexa-app/blob/main/CHANGELOG.md) for the latest changes.

- **Managed instances** (hosted by Bluesquare): the assistant uses Anthropic's Claude models served through Google Cloud Vertex AI rather than Anthropic's own API. Requests are processed in Google's `europe-west1` region in Saint-Ghislain, Belgium, so your data stays in the EU and is covered by Google Cloud's GDPR data processing terms. Google does not use your data to train models and does not share it with Anthropic. The assistant runs on Claude Opus 4.6 and conversation titles on Claude Haiku 4.5. Operators may route some tasks to other models available on Vertex AI.
- **Self-hosted instances**: each organization brings its own Anthropic API key and picks Claude Haiku 4.5, Sonnet 4.6 or Opus 4.6 in **Organization settings → AI Assistant**. Requests go directly to Anthropic under the organization's own agreement with them.
- **MCP**: whatever model your AI client uses.

## What is stored

For the built-in assistant, OpenHEXA keeps your conversations: your messages, the assistant's replies, every tool call with its input and output, token counts and the resulting cost. They are tied to your account and the workspace, and instance administrators can consult them for support and cost monitoring. For MCP, OpenHEXA logs each tool call (tool name, arguments, success or error) and when each connection was last used.

Your messages and the context described above are sent to the model provider to produce an answer. Avoid putting personal data, credentials or other sensitive information in your messages.

## Using AI responsibly

- Review every proposed change before accepting it, and read generated SQL before running it.
- Keep a person in the loop for decisions that affect people or production data.
- Grant MCP clients only the workspaces and tools they need, and revoke connections you no longer use.
- Report wrong or surprising behaviour to your administrator or on [GitHub](https://github.com/BLSQ/openhexa/issues).
