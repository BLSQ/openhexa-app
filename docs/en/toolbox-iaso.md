<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>IASO Client</h1>
</div>

[`iaso-client`](https://github.com/BLSQ/iaso-client) is the recommended Python library to fetch data from IASO. It authenticates against an IASO instance and gives typed access to organisation units, organisation unit types, forms, form versions and form submissions (instances), with automatic pagination.

!!! warning "`openhexa.toolbox.iaso` is deprecated"
    The `IASO` class from `openhexa.toolbox.iaso` is no longer maintained. Use `iaso-client` for new pipelines and notebooks, and migrate existing code when you can (see [Migrating from `openhexa.toolbox.iaso`](#migrating-from-openhexatoolboxiaso)).

## Installation

`iaso-client` is pre-installed in the OpenHEXA notebook and pipeline images. To use it elsewhere (or to pin a specific version in a pipeline's `requirements.txt`):

``` sh
pip install iaso-client
```

## Usage

### Connect to an instance

Create a `IasoClient` with the base URL of the IASO instance (without a trailing slash), then call `login()`. The bearer token is stored and reused for all subsequent requests.

In an OpenHEXA workspace, store the credentials in an [IASO connection](connections.md) and read them with the SDK:

``` python
from openhexa.sdk import workspace
from iaso_client import IasoClient

con = workspace.iaso_connection("iaso-connection-identifier")

client = IasoClient(base_url=con.url.rstrip("/"))
client.login(con.username, con.password)
```

### Read data

Every resource exposes `*_list()` and `*_retrieve()` methods. `*_list()` fetches every page and returns all matching items as a list. Filters are passed as keyword arguments.

``` python
# Organisation units
org_units = client.org_units_list(org_unit_type_id=5, project=149)
org_unit = client.org_units_retrieve(org_unit_id=781)

# Organisation unit types
org_unit_types = client.org_unit_types_list(project=149)

# Forms and form versions
forms = client.forms_list(projects_ids=[149])
form = client.forms_retrieve(form_id=276)
form_versions = client.form_versions_list(form_id=276)

# Form submissions (instances)
instances = client.instances_list(form_id=276, date_from="2025-01-01")
instance = client.instances_retrieve(instance_id=12345)
```

### Get a pandas DataFrame

`*_list()` returns a list of dictionaries, which can be loaded into a DataFrame:

``` python
import pandas as pd

df = pd.json_normalize(client.instances_list(form_id=276))
```

See the [iaso-client repository](https://github.com/BLSQ/iaso-client) for the full list of filters.

## Migrating from `openhexa.toolbox.iaso`

| `openhexa.toolbox.iaso`                                   | `iaso-client`                                                        |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| `IASO(url, username, password)`                           | `client = IasoClient(base_url=url)` <br> `client.login(username, password)` |
| `iaso.get_org_units(...)`                                 | `client.org_units_list(...)`                                         |
| `iaso.get_forms(org_units=[...], projects=[...])`         | `client.forms_list(org_unit_id=..., projects_ids=[...])`             |
| `iaso.get_form_instances(..., as_dataframe=True)`         | `pd.json_normalize(client.instances_list(...))`                      |
