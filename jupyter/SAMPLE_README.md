# Welcome to Habari!

Welcome to Habari, the Bluesquare Data Science platform.

## 🚧 Habari is alpha/beta software

This platform is a work in progress, and cannot be considered stable yet. Be prepared for some major changes 
along the way.

**Make sure to read the following sections**, as they contain important information about how to use (and not to use) 
the platform.

## 🚓 An important note about sensitive data

At this stage, the Habari platform is not specifically equipped to deal with sensitive data (for example data that contains 
personal information).

**Never upload sensitive or personal data on the Habari platform.**

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

# Read data
df = pd.read_csv("s3:some-workspace-name-lake/a-file.csv")

# Write data
df.to_csv("s3:some-workspace-name-lake/another-file.csv")
```

**Pro tip**: you can copy the path to an existing file in this bucket by right-clicking on it and selecting the 
"Copy path" menu item.

Please **do not store notebooks** in this bucket.

### The "shared notebooks" bucket

This S3 bucket is accessible from the file browser under a name that looks like `s3:some-workspace-name-notebooks`.

This bucket can be used to **share notebooks** with your whole team.

It is ok to store data files along with your notebooks here, but for data that you want to share with your team, the 
"data lake" bucket is the preferred location.

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