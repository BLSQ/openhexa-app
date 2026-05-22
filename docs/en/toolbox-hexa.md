<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>OpenHEXA Toolbox - OpenHEXA Client (no longer maintained)</h1>
</div>

_⚠️ We now recommend using the [SDK OpenHexa Client](sdk.md#using-the-openhexa-client) instead. It contains plenty of (typed) methods and can be semi-automatically extended by the OpenHexa team. The toolbox client will not be maintained/extended in the future_

The OpenHEXA class is part of the OpenHexa toolbox, designed for interacting with the OpenHexa platform's API.
The OpenHEXAClient module enables users to interact with the OpenHEXA backend using GraphQL syntax.

## Installation

``` sh
pip install openhexa.toolbox
```

## Usage

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
