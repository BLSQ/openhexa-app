<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>IASO Client</h1>
</div>

[`iaso-client`](https://github.com/BLSQ/iaso-client) is the recommended Python library to fetch data from IASO. It authenticates against an IASO instance and gives typed access to organisation units, organisation unit types, forms, form versions and form submissions (instances), with automatic pagination, pandas DataFrame output and CSV/XLSX exports.

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

Every resource exposes `*_list()` and `*_retrieve()` methods. Filters are passed as keyword arguments.

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

### Pagination

- `*_list()` fetches and aggregates results across all pages.
- `*_list(page=...)` returns a single page of results (JSON only).
- `max_page_size` controls the page size and must be between `50` and `2000`.

``` python
first_page = client.org_units_list(page=1, max_page_size=500)
```

### Get a pandas DataFrame

``` python
df = client.instances_list(form_id=276, format="dataframe")
```

### Export to CSV or XLSX

Org units, forms and instances can be exported directly to a file using IASO's export endpoints:

``` python
client.org_units_list(format="csv", output_path=f"{workspace.files_path}/org_units.csv")
client.instances_list(format="xlsx", form_id=276, output_path=f"{workspace.files_path}/submissions")
```

`output_path` must be a file path: its parent directory must exist and the file must not already exist. The `.csv` or `.xlsx` extension is added if omitted.

### Endpoints without a typed method

Use `raw()` to call any IASO `GET` endpoint relative to `/api/`:

``` python
entities = client.raw("entities/", params={"entity_type_ids": 12}, page=1, max_page_size=100)
```

See the [iaso-client repository](https://github.com/BLSQ/iaso-client) for the full list of methods and filters.

## Migrating from `openhexa.toolbox.iaso`

| `openhexa.toolbox.iaso`                                   | `iaso-client`                                                        |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| `IASO(url, username, password)`                           | `client = IasoClient(base_url=url)` <br> `client.login(username, password)` |
| `iaso.get_org_units(...)`                                 | `client.org_units_list(...)`                                         |
| `iaso.get_forms(org_units=[...], projects=[...])`         | `client.forms_list(org_unit_id=..., projects_ids=[...])`             |
| `iaso.get_form_instances(..., as_dataframe=True)`         | `client.instances_list(..., format="dataframe")`                     |
| `iaso.get_projects()`                                     | `client.raw("projects/")`                                            |
