<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>OpenHEXA Client</h1>
</div>

The OpenHEXA SDK ships a typed `OpenHexaClient` to interact programmatically with the OpenHEXA platform — workspaces, pipelines, runs, datasets and webapps — with full type hints. It replaces the legacy `openhexa.toolbox.hexa` client.

The full set of typed methods is documented in the [SDK guide](sdk.md#using-the-openhexa-client); this page covers installation, authentication, and a short tour. The legacy `openhexa.toolbox.hexa` client is kept at the bottom for reference.

## Installation

The client is part of the `openhexa.sdk` package:

```sh
pip install openhexa.sdk
```

## Authentication

Inside OpenHEXA notebooks and pipelines, the client is configured automatically from the `HEXA_SERVER_URL` and `HEXA_TOKEN` environment variables. When running locally, set those variables yourself (e.g. via `openhexa config set_url` and `openhexa config set_token`) or instantiate the client explicitly:

```python
from openhexa.sdk import OpenHexaClient

client = OpenHexaClient(server_url="https://app.demo.openhexa.org", token="your-token")
```

## Usage

The recommended entry point is the ready-to-use `openhexa` instance, which picks up the environment configuration:

```python
from openhexa.sdk.client import openhexa

workspaces_response = openhexa.workspaces()
for workspace in workspaces_response.items:
    print(f"{workspace.slug} — {workspace.name}")

pipelines_response = openhexa.pipelines(workspace_slug="my-workspace", page=1, per_page=10)
for pipeline in pipelines_response.items:
    print(f"{pipeline.code}: {pipeline.name}")

pipeline_details = openhexa.pipeline(workspace_slug="my-workspace", pipeline_code="bikes-in-brussels")
if pipeline_details:
    print(f"Schedule: {pipeline_details.schedule}")

datasets_response = openhexa.datasets(page=1)
for dataset in datasets_response.items:
    print(f"{dataset.slug} — {dataset.name}")
```

The client exposes a large number of typed methods, easing discoverability and integration:

![Screenshot 2025-06-27 at 17 00 07](https://github.com/user-attachments/assets/cd2e530e-ba4f-46d5-aa4f-695ae52eb92c)

See the [SDK guide](sdk.md#using-the-openhexa-client) for end-to-end examples (managing pipelines, datasets, runs, and webapps).

---

## Deprecated: `openhexa.toolbox.hexa`

> ⚠️ **Deprecated** — the `openhexa.toolbox.hexa.OpenHEXA` GraphQL client is no longer maintained. Use the `OpenHexaClient` above for any new code, and migrate existing usage when possible. The content below is kept only as a reference for projects that still depend on it.

### Installation

```sh
pip install openhexa.toolbox
```

### Connect to the API

To initialize the OpenHEXA class, you need to provide the server_url of the OpenHexa instance and either a username/password combination or an API token for authentication.
Two-factor authentication should be disabled for this method.

```python
from openhexa.toolbox.hexa import OpenHEXA
# We can authenticate using username / password
hexa = OpenHEXA("https://app.demo.openhexa.org", username="username",  password="password")

# You can also use the token provided by OpenHEXA on the pipelines page.
hexa = OpenHEXA("https://app.demo.openhexa.org", token="token")
```

### Play with the API

After importing Hexa module, you can use provided method to fetch Projects, Organisation Units and Forms that you have
permissions for.

```python
from openhexa.toolbox.hexa import OpenHEXA
# Get workspaces
workspaces = hexa.get_workspaces()

# Get pipelines in a specific workspace
workspace_slug = workspaces['workspaces']['items'][0]['slug']
pipelines = hexa.get_pipelines(workspace_slug)

# Run a pipeline
pipeline_id = pipelines['pipelines']['items'][0]['id']
run_response = hexa.run_pipeline(id=pipeline_id,config={}, send_notification=True)

print(run_response)
```