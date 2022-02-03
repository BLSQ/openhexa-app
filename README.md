<div align="center">
   <img alt="OpenHexa Logo" src="https://raw.githubusercontent.com/BLSQ/openhexa-app/main/hexa/static/img/logo/logo_with_text_grey.svg" height="80">
</div>
<p align="center">
    <em>Open-source Data integration platform</em>
</p>
<p align="center">
   <a href="https://github.com/BLSQ/openhexa-app/actions/workflows/test.yml">
      <img alt="Test Suite" src="https://github.com/BLSQ/openhexa-app/actions/workflows/test.yml/badge.svg">
   </a>
</p>

OpenHexa App Component
======================

OpenHexa is an **open-source data integration platform** that allows users to:

- Explore data coming from a variety of sources in a **data catalog**
- Schedule **data pipelines** for extraction & transformation operations
- Perform data analysis in **notebooks**
- Create rich data **visualizations**

<div align="center">
   <img alt="OpenHexa Screenshot" src="https://test.openhexa.org/img/screenshot_catalog.png" hspace="10" height="150">
   <img alt="OpenHexa Screenshot" src="https://test.openhexa.org/img/screenshot_notebook.png" hspace="10" height="150">
</div>

OpenHexa architecture
=====================

The OpenHexa platform is composed of **three main components**:

- The **App component**, a Django application that acts as the user-facing part of the OpenHexa platform
- The **Notebooks component** (a customized [JupyterHub](https://jupyter.org/hub) setup)
- The **Data Pipelines component** (built on top of [Airflow](https://airflow.apache.org/))

This repository contains the code for the **App component**, which serves as the user-facing part of the OpenHexa
stack.

The code related to the Notebooks component can be found in the
[`openhexa-notebooks`](https://github.com/blsq/openhexa-notebooks) repository, while the Data Pipelines component
code resides in the [`openhexa-pipelines`](https://github.com/blsq/openhexa-pipelines) repository.

App component overview
----------------------

The **App component** is a [Django](https://www.djangoproject.com/) application connected to a
[PostgreSQL](https://www.postgresql.org/) database.

The **App component** is the main point of entry to the OpenHexa platform. It provides:

- User management capabilities
- A browsable Data Catalog
- An advanced search engine
- A dashboard

Additionally, it acts as a frontend for the **Notebooks** component (which is embedded in the app component as an
iframe) and for the **Data pipelines** component.

OpenHexa can connect to a wide range of **data stores**, such as AWS S3 / Google Cloud GCS buckets,
DHIS2 instances, PostgreSQL databases...

**Data stores** in OpenHexa can be categorized under three different categories:

1. **Primary Data Sources**: those data sources are external to the platform. They are **read-only**: OpenHexa will
   never alter the data residing in primary data sources. Users can schedule data extracts in **data lakes**
   or **data warehouses** to work on the extracted data.
1. **Data Lakes**: those data stores are buckets of flat files of various formats (CSV, GPKG, Jupyter
   notebooks...). Data residing in data lakes can be read and written to.
1. **Data Warehouses**: those data stores are read/write databases (as of now, only PostgreSQL data warehouses are
   implemented).

Running OpenHexa
================

Docker image
------------

The OpenHexa app Docker image is publicly available on Docker Hub
([blsq/openhexa-app](https://hub.docker.com/r/blsq/openhexa-app)).

This repository also provides a Github workflow to build the Docker image in the `.github/workflows` directory.

Local development
-----------------

In addition to the **App component** Docker image, we also provide a `docker-compose.yaml` file for local development.

The following steps will get you up and running:

```bash
docker-compose build
docker-compose run app fixtures
docker-compose up
```

This will start all the required services and processes, correctly configure all the environment variables
and fill the database with some initial data.

You can then log in with the following credentials: `root@openhexa.org`/`root`

Python requirements are handled with [pip-tools](https://github.com/jazzband/pip-tools), you will need to install it. 
When you want to add a requirement, simply update `requirements.in` and run `pip-compile` in the root directory. You 
can then rebuild the Docker image.

### Running commands on the container

The app Docker image contains an entrypoint. You can use the following to list the available commands:

```bash
docker-compose run app help
```

As an example, use the following command to run the migrations:

```bash
docker-compose run app migrate
```

### Running the tests

Running the tests is as simple as:

```bash
docker-compose run app test
```

Some tests call external resources (such as the public DHIS2 API) and will slow down the suite. You can exclude them
when running the test suite for unrelated parts of the codebase:

```bash
docker-compose run app test --exclude-tag=external
```

Test coverage is evaluated using the [`coverage`](https://github.com/nedbat/coveragepy) library:

```bash
docker-compose run app coveraged-test
```

If you have the .coverage generated, you can also create html report with the command
```coverage html```.

### Code style

Our python code is linted using [`black`](https://github.com/psf/black), [`isort`](https://github.com/PyCQA/isort) and [`autoflake`](https://github.com/myint/autoflake).
We currently target the Python 3.9 syntax.

We use a [pre-commit](https://pre-commit.com/) hook to lint the code before committing. Make sure that `pre-commit` is
installed, and run `pre-commit install` the first time you check out the code. Linting will again be checked
when submitting a pull request.

You can run the lint tools manually using `pre-commit run --all`.

OpenHexa uses [TailwindUI](https://tailwindui.com/), [TailwindCSS](https://tailwindcss.com/)
and [Heroicons](https://heroicons.com/) for the user interface.
