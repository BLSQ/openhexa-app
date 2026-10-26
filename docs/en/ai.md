<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>AI in OpenHEXA</h1>
</div>
</div>

OpenHEXA integrates Large Language Models (LLMs) in two ways: through the **built-in assistant**, which helps you create and edit pipelines, web apps, and SQL queries directly within the platform, and through an **MCP server**, which allows an external AI client of your choice (Claude, ChatGPT, Gemini CLI...) to interact with your workspaces. This page explains what each integration does, what data it can access, and which models power it.

!!! warning "AI can make mistakes"
    Generated code, queries, and answers can be inaccurate, incomplete, or outdated. Always review any AI proposal before accepting, running, or sharing it.

## How AI is used

### The built-in assistant

The assistant is available in the workspaces of an organization where an administrator has enabled it (**Organization settings → AI Assistant**). It assists with specific, well-defined tasks in a few key places:

| Where | What it does |
| --- | --- |
| **Pipelines → Create → Create with AI** | Generates a new pipeline and the initial version of its code from your description. |
| **Pipeline code editor → chat panel** | Reads the pipeline's files and proposes updates or a new version. Nothing is saved until you review and accept the proposal. |
| **Web Apps → Create → Create with AI** | Generates a static web app from your description, then opens it in the code editor. |
| **Web app code editor → chat panel** | Reads the web app's files and proposes updates, which you can review and accept before saving. |
| **Data Studio → Generate SQL** | Translates a natural language question into a single read-only `SELECT` query. The model only sees the database schema (table and column names and types)—never the data in the tables. Before displaying the query, the database generates an execution plan to catch syntax errors without running it. The query only runs when you choose to execute it. |

A lightweight model also automatically gives each conversation a short title.

The assistant runs with dedicated system instructions for each task and declines requests unrelated to OpenHEXA. It cannot run pipelines, execute SQL on its own initiative, modify permissions, or access anything outside the active workspace.

Each organization has a monthly AI budget set by its subscription. When this budget is reached, the AI features are paused for the whole organization until the start of the next month.

### The MCP server

OpenHEXA provides a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server so that external AI assistants can inspect and interact with your workspaces. Setup instructions for supported clients are available at `/mcp/wiki` on your OpenHEXA instance (for example, <https://app.openhexa.org/mcp/wiki>), and the full tool catalogue is at `/mcp`.

Connecting a client works through OAuth: the client redirects you to OpenHEXA, where you sign in and select exactly which workspaces it may access and which tools it may call. You can restrict or revoke these permissions at any time from **Account → MCP connections**. Changes take effect on the next tool call.

With MCP, the underlying model is chosen and run by your external AI client, not OpenHEXA. Anything returned by a tool (such as file contents, dataset previews, or pipeline code) is sent to that client and processed under its provider's terms of service. Only grant access to the workspaces and tools you actually need.

## What the AI can access

In both cases, the AI acts **on your behalf**: every tool call goes through the same permission checks as the OpenHEXA web interface, meaning the AI can never view or modify anything beyond what your account is allowed to access. An MCP connection is further restricted to the specific workspaces and tools you explicitly grant.

### Built-in assistant

| Task | Reads | Writes |
| --- | --- | --- |
| Create / edit pipeline | Workspace metadata and description, datasets and dataset file previews, workspace files, connection names and field names (never secret values), the pipeline's code and files, OpenHEXA documentation | Creates the pipeline (creation); proposes updates or a new version for you to accept (editing) |
| Create / edit web app | Same as pipelines, plus the database schema (tables and columns, never rows), saved queries, the workspace pipeline list, and the web app's files | Creates the web app; creates or updates saved queries; proposes updates for you to accept |
| Generate SQL | Only the database schema: table and column names and types. It never reads the rows of any table, and no query result is ever sent to the model | Nothing: the query is only displayed for you to review |

If the workspace has a description, it is provided to the assistant as background context. Workspace administrators can use it to document data conventions or context, but the assistant treats it as informative context, not as instructions that can override its guidelines.

### MCP server

Tools are grouped by resource. Each grant covers one resource group, with read and write tools authorized separately:

| Resource | Read tools | Write tools |
| --- | --- | --- |
| Workspaces | list, get | update |
| Files | list, read | write |
| Datasets | list, get, preview files | create datasets and versions |
| Pipelines | list, get, get run | run, update, create, create version |
| Pipeline templates | list, get | create pipeline from template |
| Web apps | list, get, read files | create, update, edit files |
| Databases | schema of tables and columns (not rows) | — |
| Saved queries | list, get SQL | create, update |
| Connections | list names, types, and field names (never secret values) | — |

Only the help tool, which returns OpenHEXA documentation, works without a grant. No MCP tool can execute SQL against a workspace database or access connection secrets.

## Models

!!! info "Models evolve over time"
    Language models change quickly. The models listed below are in use at the time of writing; OpenHEXA updates them as faster, more capable, or more cost-effective options become available, without altering the assistant's workflow. Check the [release notes](https://github.com/BLSQ/openhexa-app/blob/main/CHANGELOG.md) for recent updates.

- **Managed instances** (hosted by Bluesquare): The assistant uses Anthropic's Claude models served through Google Cloud Vertex AI rather than Anthropic's direct API. Requests are processed in Google's `europe-west1` region in Saint-Ghislain, Belgium, ensuring your data remains within the EU under Google Cloud's GDPR data processing terms. Google does not use your data to train models and does not share it with Anthropic. The assistant is powered by Claude Opus 4.6, and conversation titles are generated with Claude Haiku 4.5. Instance operators may route certain tasks to other models supported on Vertex AI.
- **Self-hosted instances**: Each organization provides its own Anthropic API key and selects Claude Haiku 4.5, Sonnet 4.6, or Opus 4.6 in **Organization settings → AI Assistant**. Requests are sent directly to Anthropic under the organization's own terms and service agreement.
- **MCP**: The model is determined entirely by whichever AI client you connect.

## What is stored

For the built-in assistant, OpenHEXA stores your conversations: your messages, the assistant's replies, every tool call along with its inputs and outputs, token counts, and the resulting cost. This history is associated with your account and the workspace; instance administrators can review it for technical support and cost monitoring. For MCP, OpenHEXA logs each tool call (tool name, arguments, success or error status) and records when each connection was last used.

Your messages and the context described above are sent to the model provider to generate responses. Avoid including personal data, credentials, or other sensitive information in your prompts.

## Using AI responsibly

- Review every proposed change before accepting it, and inspect generated SQL queries before running them.
- Keep a human in the loop for decisions that affect people or production data.
- Grant MCP clients only the workspaces and tools they strictly need, and revoke connections you no longer use.
- Report any inaccurate, unexpected, or unintended behaviour to your administrator or on [GitHub](https://github.com/BLSQ/openhexa/issues).
