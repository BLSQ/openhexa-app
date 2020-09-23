# Welcome to Habari!

Welcome to Habari, the Bluesquare Data Science platform.

## 🚧 Habari is alpha/beta software

This platform is a work in progress, and cannot be considered stable yet. Be prepared for some major changes 
along the way.

**Make sure to read the following sections**, as they contain important information about how to use (and not to use) 
the platform.

## 🚒 An important note about sensitive data

At this stage, the Habari platform is not equipped to deal with sensitive data (for example data that contains personal 
information).

**Never upload sensitive or personal data on the Habari platform.**

## 🚓 An important note about credentials

In the course of your work on the platform, you might need access to specific APIs and databases. Those external 
resources often require credentials.

**Never store those credentials in any form on the platform**.

First, consider whether the data that you want to access can be extracted in a dedicated, secure data pipeline 
outside Habari.

If it is not the case, and you really need to access a protected external resource, use a password prompt so 
that credentials are not leaked in the file itself or in the notebook output.

Here is an example for Python - for R, consider using [getPass](https://github.com/wrathematics/getPass).

```python
import getpass

API_KEY = getpass.getpass("API key")
API_SECRET = getpass.getpass("API secret")

# later on
call_api(API_KEY, API_SECRET, "some_param")
```

Avoid printing the credentials, as they would be stored in the notebook output.

Once you are satisfied with such an extraction process, especially if it is a recurring task, please 
consider moving it to an external data pipeline.

## 💽 File storage

Habari allows you to store files in 3 different locations:

1. A **"data lake"** bucket: shared data in flat files (CSV, json, etc...)
1. A **"shared notebooks"** bucket: Jupyter notebooks that you want to share with your colleagues
1. A **personal filesystem**: for your personal drafts and temporary data

### The "data lake" bucket

This S3 bucket is accessible from the file browser under a name that looks like `s3:some-workspace-name-lake`.

This bucket can be used to access and read **shared data**.

Data in this bucket can be loaded into your dataframes. As an example, using Python/Pandas:

```python
import pandas as pd

# Read data - note the double slash after s3:
df = pd.read_csv("s3://some-workspace-name-lake/a-file.csv")

# Write data - note the double slash after s3:
df.to_csv("s3://some-workspace-name-lake/another-file.csv")
```

**Pro tip**: you can copy the path to an existing file in this bucket by right-clicking on it and selecting the 
"Copy path" menu item. 

Don't forget to add a **double slash** after the `s3:` prefix at the beginning of the file (this feature will be improved 
in the future so that the copied path can be used right away).

Please **do not store notebooks** in this bucket.

### The "shared notebooks" bucket

This S3 bucket is accessible from the file browser under a name that looks like `s3:some-workspace-name-notebooks`.

This bucket can be used to **share notebooks** with your whole team.

It is ok to store data files along with your notebooks here, but for data that you want to share with your team, the 
"data lake" bucket is the preferred location.

There is **no version control** for notebooks at this point. Communicate with your teammates and make sure 
that you are not working on the same notebooks at the same time, otherwise you might end up overwriting your 
colleague's notebook.

**Pro tip**: As this bucket is backed up on a regular basis, this is the best place to store your work.

### Personal filesystem

Any file or folder that you create outside the two buckets mentioned above are stored in a personal filesystem. Those 
files are not shared with your team.

As this filesystem is faster than the S3 buckets, it is ideal for your work in progress.

**Pro tip**: While Habari is in alpha/beta state, we encourage you to "back up" your notebooks in the "shared notebooks" 
bucket.

## 🗂 The exploration database

**Never store sensitive or personal information in the exploration database**.

Habari allows you to store data in an **exploration database**.

This database can be accessed by external BI tools such as Tableau or Power BI.

To allow you to access this database from your notebook code, Habari puts a series of environment variables at your 
disposal:

* A ready-to-use connection string for Pandas/SQLAlchemy: `EXPLORE_DB_URL`
* A series of parameters to use in other contexts (R, BI tool configuration, etc...):
    * `EXPLORE_DB_USER`
    * `EXPLORE_DB_PASSWORD`
    * `EXPLORE_DB_HOST`
    * `EXPLORE_DB_PORT`
    * `EXPLORE_DB_NAME`
    
To print them all at once (Python):

```python
import os

for key in ["HOST", "PORT", "NAME", "USER", "PASSWORD"]:
    print(f"{key}: {os.environ['EXPLORE_DB_' + key]}")
```
    
Here is a Python/Pandas code sample to read/write from/to the database:

```python
import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.environ["EXPLORE_DB_URL"])

# Read data
df = pd.read_sql('table_name', con=engine)

# Write data
df.to_sql('table_name', con=engine, if_exists="replace")
```