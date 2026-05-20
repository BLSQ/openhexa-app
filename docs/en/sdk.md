<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Using the OpenHEXA SDK</h1>
</div>
</div>

The OpenHEXA Python SDK is a tool that helps you write code for the OpenHEXA platform.

It is particularly useful to write OpenHEXA data pipelines, but can also be used in the OpenHEXA notebooks environment.

## Getting started

The OpenHEXA SDK is installed by default in your OpenHEXA notebooks environment (see [Using notebooks in OpenHEXA](notebooks-advanced.md) for more information).

If you only want to use it in Jupyter notebooks, you don't have to install anything yourself.

If you want to run OpenHEXA pipelines locally, please refer to the [Writing OpenHEXA pipelines](writing-pipelines.md) guide for installation instructions.


## Reading and writing files

In your notebook and pipeline environment, two directories are exposed:

1. The `workspace` directory
1. The `tmp` directory

## The workspace directory

The `workspace` directory is the shared workspace filesystem, this is where most of your work should take place. The content of this directory corresponds to what you can see in the **Files** tab of the OpenHEXA interface (see the [File management in workspaces](files.md) section in the user manual for more information).

The workspace filesystem is mounted as a regular filesystem in your notebook and pipeline environments - in other words, there is nothing special to do to work with workspace files (although there are some performance considerations to keep in mind, see below).

The SDK provides a simple property on the `workspace` global object to get the workspace filesystem path: `workspace.files_path`. We recommend that you use this property when writing or reading files, instead of relying on hard-coded paths or relative paths.

Here is a simple example:

```python
from openhexa.sdk import workspace
import pandas as pd

# Read data
df = pd.read_csv(f"{workspace.files_path}/covid_data.csv")

# Write data
df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
df.to_csv(f"{workspace.files_path}/foobar.csv")
```

## The tmp directory

⚠️ The `tmp` directory is not persistent - all of its content will be deleted when your Jupyter server shuts down.

The `tmp` directory, as it name suggests, is for temporary data. You can use it as an ephemeral file system for caching or debugging purposes, or for temporary downloads.

Additionally, in some rare cases, the shared workspace directory can't be used for some write operations. This can happen when using specific libraries. In those situations, you can use the `tmp` folder for writing, and then copy the required files from the `tmp` directory to the `workspace` directory.

You can get the absolute path to the `tmp` directory using the `workspace.tmp_path` property.

## Implementation and performance considerations

Behind the scenes, the workspace filesystem uses an object storage system (usually [Google Cloud Storage](https://cloud.google.com/storage) buckets) mounted with a [FUSE](https://en.wikipedia.org/wiki/Filesystem_in_Userspace) interface. In most cases, you don't need to worry about this implementation detail. However, while the read and write performance of such a setup is usually satisfactory, you might encounter performance issues when performing a large number of small write or read operations.

One example of such a scenario is opening a file and performing a large number of writes in append mode. If you notice a significant execution slowdown while attempting to do this, you might want to consider alternatives:

- Building the file content in-memory and writing it in a single pass
- Using the `tmp` directory for the append writes, and copying the file to the `workspace` directory afterwards

## Using the workspace database

Every workspace comes with a ready-to-use [PostgreSQL](https://www.postgresql.org/) database. You can find general information regarding this database in the [user manual](database.md).

The [PostGIS](https://postgis.net/) geospatial extension is installed on every workspace database.

## Basics

The OpenHEXA SDK doesn't do much for database operations ; it simply allows you to easily get the database credentials, 
that you can then use however you see fit using your favourites libraries.

Reading from or writing to the workspace database can be done using the `workspace` helper:

```python
import pandas as pd
from sqlalchemy import create_engine, Integer, String
from openhexa.sdk import workspace

# Create a SQLAlchemy engine
engine = create_engine(workspace.database_url)

# Read data
pd.read_sql("SELECT * FROM covid_data", con=engine)

# Write data
df = pd.DataFrame({"foo": [1, 2, 3], "bar": ["A", "B", "C"]})
df.to_sql("a_new_table", con=engine, if_exists="replace", index_label="id", chunksize=100, 
          dtype={"foo": Integer(), "bar": String()})
pd.read_sql("SELECT * FROM a_new_table", con=engine)
```

In this example, we use the 
[`pandas.Dataframe.to_sql`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html) method to write
data to the workspace database. You are of course free to use any other library that can connect to a PostgreSQL 
database.

By default, all rows will be written at once when calling `to_sql()`, which can result in high memory usage.
Hence, we encourage the usage of the `chunksize` argument like in the above example, which allows you to choose the 
number of rows in each batch to be written at a time.

When dealing with a small number of rows, for simple use cases and experimentations, we also encourage you to use the `dtype` argument to explicitly specify the PostgreSQL column types. If you don't, pandas will try to guess the Postgres column types from the pandas dataframe column types, which can lead to unexpected type conversions.

## Managing your data model with columns and indexes

As soon as you are dealing with a significant row count, you should consider defining your data model explicitly and using [Database indexes](https://www.postgresql.org/docs/current/indexes.html). You are free to chose how you want to deal with indexes creation and maintenance. Here is an example using [SQLALchemy metadata](https://docs.sqlalchemy.org/en/20/core/metadata.html):

```python
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from openhexa.sdk import workspace
import pandas as pd

engine = create_engine(workspace.database_url)
metadata_obj = MetaData()

# Define "letter frequency" table and indexes
letter_frequency = Table(
    "letter_frequency",
    metadata_obj,
    Column("letter", String(1), primary_key=True),
    Column("frequency", Integer(), nullable=False, index=True),
    Column("percentage", Float, nullable=False),
)
metadata_obj.create_all(engine)

# Prepare data
df = pd.read_csv(f"{workspace.files_path}/letter_frequency.csv")
df["Letter"] = df["Letter"].str.replace('"', "")
df["Letter"] = df["Letter"].str.strip()
df = df.rename(columns={"Letter": "letter", ' "Frequency"': "frequency", ' "Percentage"': "percentage"})
df = df.set_index("letter")
df

# Save to database
# con.execute("DELETE FROM...")
df.to_sql("letter_frequency", index_label="letter", con=engine, if_exists="append", dtype={"letter": String(1), "frequency": Integer(), "percentage": Float()})
```

## Using connections

The `workspace` helper offers several tools for accessing the different [connections](connections.md) available in OpenHEXA.

The following table shows, for each connection type, the associated method name on the `workspace` helper, and the available fields:

|  Type               |  Method name          |   Field(s)                                                         |
| ------------------- | --------------------- | ------------------------------------------------------------------ |
| DHIS2               | dhis2_connection      |  `url` <br> `username` <br> `password`                             |
| PostgreSQL          | postgresql_connection |  `username` <br> `password` <br> `host` <br> `port` <br>`database_name`  |
| Amazon S3 Bucket    | s3_connection         |  `bucket_name` <br> `access_key_id`  <br> `secret_access_key`      |
| Google Cloud Bucket | gcs_connection        |  `bucket_name` <br> `service_account_key`                          |
| Iaso                | iaso_connection       |  `url` <br> `username` <br> `password`                             | 
| Custom              | custom_connection     |  See below                                                         |

You can then use the `workspace` helper to fetch a connection:

```python
from openhexa.sdk import workspace
import requests

dhis2_conn = workspace.dhis2_connection("conn-identifier")  # The identifier can be found in the connection detail screen
response = requests.get(f"{dhis2_conn.url}/api/...")

custom_conn = workspace.custom_connection("another-conn-identifier")

# or you can use the unified API for getting connection helper
iaso_conn = workspace.get_connection("identifier")

# The actual fields will vary depending on the fields you have defined on your custom connection
response = requests.get(f"{custom_conn.server_url}/{custom_conn.api_version}")
```

## Working with datasets

Here is an example of how to use the OpenHEXA SDK to work with a dataset:

```python
import pandas as pd
from openhexa.sdk.workspaces import workspace
from io import StringIO

# Create a new dataset
dataset = workspace.create_dataset("Test dataset", "Description")
print(dataset.slug)
# If the dataset already exists
# dataset = workspace.get_dataset("test-dataset-42b690") 

# Loop over the files within the latest version
for file in dataset.latest_version.files:
    print((file.filename, file.created_at))

# Get a single file
cities = dataset.latest_version.get_file("cities.csv")
cities_df = pd.read_csv(cities.download_url)

# Download the file
with open(f"{workspace.files_path}/cities.csv", "wb") as cities_file:
    cities_file.write(cities.read())

# Loop over the existing versions
for version in dataset.versions:
    print(version.name)

# Create a new version
version = dataset.create_version("v1")

# Add a file by path
version.add_file(f"{workspace.files_path}/cities.csv", filename = "cities.csv")

# Check of file exists 
version.exists("cities.csv")

# Add a file on the fly using StringIO
df = pd.DataFrame({"name": ["Jane", "Jim", "Julia"], "age": [19,28,33]})
version.add_file(StringIO(df.to_csv(index=False)), filename="people.csv")
```

Datasets can also be provided as parameters to a pipeline, and can be used to store the output of a pipeline. For more information, see the [Writing OpenHEXA pipelines](writing-pipelines.md) guide.


## Working with webapps

Webapps are web applications linked to your workspace. You can retrieve webapp information programmatically using the OpenHEXA SDK.

The `workspace` helper provides a method to get webapp information by its slug identifier:

```python
from openhexa.sdk import workspace

# Get a webapp by its slug
webapp = workspace.get_webapp("my-dashboard")

# Access webapp properties
print(f"Name: {webapp.name}")
print(f"URL: {webapp.url}")
print(f"Description: {webapp.description}")
print(f"Icon: {webapp.icon}")
print(f"Is Favorite: {webapp.is_favorite}")

# Access creator information
print(f"Created by: {webapp.created_by.display_name}")
print(f"Creator email: {webapp.created_by.email}")

# Access workspace information
print(f"Workspace: {webapp.workspace.name}")

# Check permissions
if webapp.permissions.update:
    print("You can update this webapp")
if webapp.permissions.delete:
    print("You can delete this webapp")
```

If you need more control or want to use the GraphQL client directly, you can also use the `OpenHexaClient`:

```python
from openhexa.sdk import OpenHexaClient

client = OpenHexaClient()
webapp = client.get_webapp_by_slug(
    workspace_slug="my-workspace",
    webapp_slug="my-dashboard"
)

if webapp:
    print(f"Found webapp: {webapp.name}")
    print(f"URL: {webapp.url}")
else:
    print("Webapp not found")
```

The webapp slug can be found in the webapp's detail page in the OpenHEXA interface.


## Using the OpenHEXA Client

The OpenHEXA SDK provides a client interface that allows you to programmatically interact with the OpenHEXA platform to manage workspaces, pipelines, datasets, and other resources.

You benefit from a large number of typed methods, easing discoverability and integrations : 

![Screenshot 2025-06-27 at 17 00 07](https://github.com/user-attachments/assets/cd2e530e-ba4f-46d5-aa4f-695ae52eb92c)


## Basic Usage

```python
  from openhexa.sdk.client import openhexa

  # The client is automatically configured using environment variables
  # HEXA_SERVER_URL and HEXA_TOKEN (set in notebooks/pipelines)

  workspaces_response = openhexa.workspaces()

  for workspace in workspaces_response.items:
      print(f"Workspace: {workspace.name} ({workspace.slug})")
      print(f"  Description: {workspace.description}")
      print(f"  Countries: {workspace.countries}")
```

## Example of use case : a pipeline waiting for the last runs to be done
```python
from time import sleep

from openhexa.graphql import PipelineRunStatus
from openhexa.sdk import pipeline, workspace as current_workspace, current_run
from openhexa.sdk.client import openhexa

POLL_INTERVAL = 10


@pipeline(name="patient_pipeline")
def patient_pipeline():
    """A simple patient pipeline that waits for other runs to complete."""
    current_run.log_info("Started waiting for my turn")
    while len([run for run in openhexa.pipeline(workspace_slug=current_workspace.slug, pipeline_code="patient-pipeline").runs.items if run.status == PipelineRunStatus.running]) > 1:
        current_run.log_info(f"Still waiting... checking again in {POLL_INTERVAL}s")
        sleep(POLL_INTERVAL)
    current_run.log_info("No running pipeline, proceeding...")

if __name__ == "__main__":
    patient_pipeline()
```
## Managing Pipelines
```python
  from openhexa.sdk.client import openhexa

  pipelines_response = openhexa.pipelines(workspace_slug="testabcd", page=1, per_page=10)
  print(f"Pages: {pipelines_response.total_pages}")

  for pipeline in pipelines_response.items:
      print(f"Pipeline: {pipeline.name} ({pipeline.code})")
      print(f"  Type: {pipeline.type}")

      if pipeline.current_version:
          print(f"  Current version: {pipeline.current_version.name}")
          print(f"  Version number: {pipeline.current_version.version_number}")

  pipeline_details = openhexa.pipeline(workspace_slug="testabcd", pipeline_code="bikes-in-brussels")
  if pipeline_details:
      print(f"Pipeline: {pipeline_details.name}")
      print(f"Schedule : {pipeline_details.schedule}")

  create_response = openhexa.create_pipeline({
      "workspaceSlug": "testabcd",
      "name": "My New Pipeline",
      "code": "my-new-pipeline"
  })

  if create_response.success:
      new_pipeline = create_response.pipeline
      print(f"Created pipeline: {new_pipeline.code}")

      pipeline_details = openhexa.pipeline(workspace_slug="testabcd", pipeline_code=new_pipeline.code)
  else:
      print(f"Failed to create pipeline: {create_response.errors}")

  if pipeline_details:
      delete_response = openhexa.delete_pipeline({"id": pipeline_details.id})
      if delete_response.success:
          print("Pipeline deleted successfully")
      else:
          print(f"Failed to delete pipeline: {delete_response.errors}")
```

## Managing Datasets with Typed Responses

```python
  from openhexa.sdk.client import openhexa

  datasets_response = openhexa.datasets(page=1)

  for dataset in datasets_response.items:
      print(f"Dataset: {dataset.name} ({dataset.slug})")
      print(f"  Created: {dataset.created_at}")
      print(f"  Updated: {dataset.updated_at}")
      print(f"  Created by : {dataset.created_by.display_name}")

  dataset = openhexa.dataset(id=datasets_response.items[0].id)
  if dataset:
      print(f"Dataset: {dataset.name}")

      if dataset.versions:
          print(f"Total versions: {len(dataset.versions.items)}")
          for version in dataset.versions.items:
              print(f"  Version: {version.name} - Created: {version.created_at}")


  create_response = openhexa.create_dataset({
      "workspaceSlug": "testabcd",
      "name": "My Dataset",
      "description": "Dataset description"
  })

  if create_response.success:
      new_dataset = create_response.dataset
      print(f"Created dataset: {new_dataset.name} (slug: {new_dataset.slug})")
```
  ## Managing Workspace Configuration
  You can get and manage workspace configuration dictionary to set and use workspace wide properties.
  Here is an example of a property `SNT_PIPELINE_COUNT` that was configured for the workspace.
  ```python
  from openhexa.sdk import workspace

  # configuration is a JSON dictionary that can be manipulated as one
  config = workspace.configuration
  if "SNT_PIPELINE_COUNT" in config:
      print(config.get("SNT_PIPELINE_COUNT"))
      # To update the property 
      config["SNT_PIPELINE_COUNT"] = 10
      workspace.configuration = config
```
## Managing Workspaces and Members

```python
from openhexa.sdk.client import openhexa

workspaces_response = openhexa.workspaces()
for workspace in workspaces_response.items:
    print(f"Workspace: {workspace.name}")

    detailed_workspace = openhexa.workspace(slug=workspace.slug)
    print(f"  Countries: {detailed_workspace.countries}")

create_response = openhexa.create_workspace({
      "name": "My New Workspace",
      "description": "Workspace for data analysis"
  })

if create_response.success:
    new_workspace = create_response.workspace
    print(f"Created workspace: {new_workspace.name}")

    invite_response = openhexa.invite_workspace_member({
        "workspaceSlug": new_workspace.slug,
        "userEmail": "newuser@bluesuqare.org",
        "role": "EDITOR"
    })
```

## Advanced usage
  If you would like to get other actions/attributes from this library, feel free to ask the OpenHexa team to include them. They have easy and automated ways to extend this library efficiently.
  In the meantime, you can execute custom GraphQL queries for advanced use cases not covered by the predefined client methods:

```python
  from openhexa.sdk.client import openhexa

  custom_query = """
  query getWorkspaceStats($workspaceSlug: String!) {
      workspace(slug: $workspaceSlug) {
          name
          slug
          datasets {
              items {
               dataset {
                name
               }
              }
          }
      }
  }
  """

  result = openhexa.execute(
      query=custom_query,
      variables={"workspaceSlug": "testabcd"}
  )
  for dataset in result.json()["data"]["workspace"]["datasets"]["items"]:
      print(f"Dataset name {dataset["dataset"]["name"]}")
```