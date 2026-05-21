<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Using Notebooks in OpenHEXA</h1>
</div>
</div>
OpenHEXA notebooks are a customized [Jupyter](https://jupyter.org/) environment preloaded with the OpenHEXA SDK and toolboxes — this guide covers the workspace filesystem, the workspace Postgres from Python and R, and S3/GCS access.

Jupyter is a flexible integrated development environment built around notebooks – documents that combine code, documentation, data and rich visualizations. It provides a fast interactive environment for prototyping and explaining code, exploring and visualizing data, and sharing ideas with others. For more information about the Jupyter stack, please refer to the [official Jupyter documentation](https://docs.jupyter.org/en/latest/).

You can use notebooks in OpenHEXA for a variety of purposes, such as :

- Explore and perform a preliminary analysis of a dataset
- Explain and illustrate an algorithm or a data model in a [literate programming](https://en.wikipedia.org/wiki/Literate_programming) fashion
- Prototype a visualization dashboard

There are a few scenarios where you might consider using [OpenHEXA data pipelines](pipelines.md) instead:

- If you want to allow non-technical users to launch a data processing workflows using a web interface
- If you want to schedule a data workflow to run at specific points in time
- When you need standard software development practices such as version control or unit tests

The OpenHEXA notebooks component works as a standard Jupyter environment, with a few nice additions, such as:

- It comes with a lot of pre-installed libraries
- The shared workspace filesystem is accessible in the Jupyter file browser
- The workspace database credentials are automatically exposed as environment variables

The present guide will walk you through the specificities of the OpenHEXA notebooks environment. You may also find the following two guides interesting:

- [Using the OpenHEXA SDK](sdk.md): the OpenHEXA SDK is a Python library that provides building blocks and helper methods to write code on OpenHEXA
- [Using the OpenHEXA Toolbox - DHIS2](toolbox-dhis2.md): Acquire and process data from DHIS2 instances
- [Using the OpenHEXA Toolbox - IASO](toolbox-iaso.md): Fetch data from IASO
- [Using the OpenHEXA Toolbox - OpenHEXA Client](toolbox-hexa.md): Legacy GraphQL client (deprecated)

## Using the workspace filesystem

When launching the notebooks environment, you can see that the Jupyter filesystem displays two directories:

1. The `tmp` directory
1. The `workspace` directory

You can only write data in these two directories: **it is not possible to create files or directories at the root** of the filesystem.

Please refer to the [SDK documentation](sdk.md#reading-and-writing-files) for more information about the `workspace` and `tmp` directories and how to use them using Python (for R users, refer to the code sample below, as we don't have a SDK for R yet).

https://github.com/BLSQ/openhexa/assets/690667/8f279c1f-c371-490f-a04f-84a97b028859

Here is a basic example showing how to read / write data to the workspace filesystem in Python:

```python
import pandas as pd
from openhexa.sdk import workspace

# Read data
df = pd.read_csv(f"{workspace.files_path}/covid_data.csv")

# Write data
df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
df.to_csv(f"{workspace.files_path}/foobar.csv")
```

The equivalent R example (until we have a SDK for R, you will have to hard-code the workspace directory path):

```r
# Read data
df <- read.csv("/home/hexa/workspace/covid_data.csv")

# Write data
x          <- 1:10
y          <- letters[1:10]
some_data <- tibble::tibble(x, y)
write.csv(some_data, "foobar.csv")
```

https://github.com/BLSQ/openhexa/assets/690667/49e53c15-c251-4283-9450-94ae9bdff9b6

## Using the workspace database

As the workspace database is a standard [PostgreSQL](https://www.postgresql.org/) database, you can use any library 
that supports PostgreSQL to use it in a notebook.

If you use Python, the recommended way to fetch the database credentials is using the [OpenHEXA SDK](sdk.md#using-the-workspace-database).

Here is a minimal Python example (with [SQLAlchemy](https://www.sqlalchemy.org/)) to get you started:

```python
import pandas as pd
from sqlalchemy import create_engine, Integer
from openhexa.sdk import workspace

# Create a SQLAlchemy engine
engine = create_engine(workspace.database_url)

# Read data
pd.read_sql("SELECT * FROM covid_data", con=engine)

# Write data
df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
df.to_sql("a_new_table", con=engine, if_exists="replace", index_label="id", 
          chunksize=100, dtype={"id": Integer(), "foo": Integer(), "bar": Integer()})
pd.read_sql("SELECT * FROM a_new_table", con=engine)
```

Note that we use the optional `chunksize` and `dtype` arguments: `chunksize` to control the number of 
rows to be written in each batch (to optimize memory usage), and `dtype` to explicitly specify PostgreSQL column types 
and avoid conversion issues caused by the default type guessing behaviour.

As we don't have a SDK for R yet, you will need to use environment variables to get the database credentials using R.

Here is how you can do it using [DBI](https://dbi.r-dbi.org/):

```r
# Initial connection
library(DBI)
con <- dbConnect(
    RPostgres::Postgres(),
    dbname = Sys.getenv("WORKSPACE_DATABASE_DB_NAME"),
    host = Sys.getenv("WORKSPACE_DATABASE_HOST"),
    port = Sys.getenv("WORKSPACE_DATABASE_PORT"),
    user = Sys.getenv("WORKSPACE_DATABASE_USERNAME"),
    password = Sys.getenv("WORKSPACE_DATABASE_PASSWORD")
)

# Write data
x          <- 1:10
y          <- letters[1:10]
some_data <- tibble::tibble(x, y)
dbWriteTable(con, "another_table", some_data, overwrite=TRUE)
df <- dbReadTable(con, "another_table")
```

## Using connections

Once you have added a new [connection](connections.md), you will be able to access its parameters in your Jupyter environment through the SDK.

Please refer to the [OpenHEXA SDK documentation](sdk.md#using-connections) for more information about how to use connections in Python, and to the [User manual](connections.md) for general information usage about connections.


Here is how you can access connection parameters using Python:

```python
import os
from openhexa.sdk import workspace

print(workspace.get_connection("connection-identifier"))
```

## Restarting your Jupyter server

There are a few situations where you might want to restart your Jupyter server as :

- Your server is completely stuck and restarting it is your last option

Unfortunately, restarting your Jupyter server is not really straightforward at the moment. This will be improved in the future. 

For now, you will have to:

1. Open the Jupyterhub control panel (`File > Hub Control Panel`, will open in a new window or tab)
1. Find you server in the list of running servers (each server in the list correspond to a workspace ; the server you are looking for is in the "running" state and its name should match the URL in your browser address bar)
1. Click on `stop`
1. Close the Hub Control panel tab, go back to the OpenHEXA notebooks screen and reload the page

https://github.com/BLSQ/openhexa/assets/690667/18a6adfe-f44f-4bac-a71f-9127657a19d6

## Tips and tricks

This section contains a few recipes that you might find useful.

## Using s3fs to interact with a S3 bucket

If you need to browse, download or upload data in an Amazon S3 bucket, the first step is to add a AWS S3 [connection](connections.md).

Once you have added the connection, you will be able to interact with the bucket in a Jupyter notebook.

While your OpenHEXA Jupyter environment comes with [boto3](https://github.com/boto/boto3) pre-installed, for most operations, using [s3fs](https://github.com/fsspec/s3fs) will be easier (`s3fs` is also pre-installed in your environment).

Here is a basic example showing how to use `s3fs` in an OpenHEXA notebook:

```python
import os
import s3fs

# The environment variable names can be copy-pasted from the connection detail page
fs = s3fs.S3FileSystem(key=os.environ["BUCKET_CONNECTION_ACCESS_KEY_ID"], secret=os.environ["BUCKET_CONNECTION_ACCESS_KEY_SECRET"])
bucket_name = os.environ["BUCKET_CONNECTION_BUCKET_NAME"]

# List the files in a directory within the bucket
fs.ls(f"{bucket_name}/data/climate")

# Download all the files from the bucket directory in the workspace filesystem
fs.get(f"{bucket_name}/data/climate", "/home/hexa/workspace/climate_data", recursive=True)
```

## Using gcsfs to interact with a Google Cloud Storage bucket

If you need to browse, download or upload data in an Google Cloud Storage bucket, the first step is to add a GCS [connection](connections.md).

Once you have added the connection, you will be able to interact with the bucket in a Jupyter notebook.

The easiest way to interact with GCS is to use [gcsfs](https://github.com/fsspec/gcsfs) (`gcsfs` is pre-installed in your environment).

Here is a basic example showing how to use `gcsfs` in an OpenHEXA notebook:

```python
import gcsfs
import os
import json

# The environment variable names can be copy-pasted from the connection detail page
gcsfs_service_account_key = json.loads(os.environ["BUCKET_CONNECTION_SERVICE_ACCOUNT_KEY"])
fs = gcsfs.GCSFileSystem(token=gcsfs_service_account_key)
bucket_name = os.environ["BUCKET_CONNECTION_BUCKET_NAME"]

# List the files in a directory within the bucket
fs.ls(f"{bucket_name}/data/population")

# Download all the files from the bucket directory in the workspace filesystem
fs.get(f"{bucket_name}/data/population", "/home/hexa/workspace/population_data", recursive=True)
```