OpenHexa (App component)
========================

OpenHexa is an open-source data integration platform that allows users to:

- Explore data coming from a variety of sources in a **data catalog**
- Schedule **data pipelines** for extraction & transformation operations
- Perform data analysis in **notebooks**
- Create rich data **visualizations**

The OpenHexa platform is composed of:

- The **App** component, a Django application that acts as the user-facing part of the OpenHexa platform
- The **Notebooks** component (a [JupyterHub](https://jupyter.org/hub) setup)
- The **Data Pipelines** component (build on top of [Airflow](https://airflow.apache.org/))

This repository contains the code for the **App** component, which servers as the user-facing part of the OpenHexa
stack.

The code related to the notebook component can be found in the
[`openhexa-notebooks`](https://github.com/blsq/openhexa-notebooks) repository, while the data pipelines code resides in
the [`openhexa-pipelines`](https://github.com/blsq/openhexa-pipelines) repository.

Architecture overview
---------------------

The **Platform** component is a [Django](https://www.djangoproject.com/) application connected to a
[PostgreSQL](https://www.postgresql.org/) database.

OpenHexa can connect to a wide range of data stores, such as AWS S3 / Google Cloud GCS buckets, DHIS2 data warehouses,
PostgreSQL databases...

This component is meant to be deployed in a [Kubernetes](https://kubernetes.io/) cluster (either in a public cloud or in
your own infrastructure).

The **App** component is the main point of entry to the OpenHexa platform. It provides:

- User management capabilities
- A browsable Data Catalog
- An advanced search engine
- A dashboard

Additionally, it acts as a frontend for the Notebooks and Data Pipelines components.

Data stores
-----------

OpenHexa handles three different types of data stores:

1. **Primary Data Sources**: those data sources are external to the platform. OpenHexa users can plug them to the
   platform so that their content can be indexed, browsed and searched. They are **read-only**: OpenHexa will never
   alter the data residing in primary data sources. Users can schedule data extracts in **data lakes**
   or **data warehouses** and work on the extracted data.
1. **Data Lakes**: those data stores are buckets of flat files of various formats (CSV, geopackages, Jupyter
   notebooks...). Data residing in data lakes can be read and written to.
1. **Data Warehouses**: those data stores are read/write databases (as of now, only PostgreSQL data warehouses are
   implemented).

**Primary Data Source** are only accessible within the **App** component. **Data Lakes** and **Data Warehouses** can be
attached to (and accessed from) the **Notebooks**component.


Provisioning and deployment
---------------------------

Note: the following instructions are tailored to a Google Cloud Platform setup (using Google Kubernetes Engine and
Google Cloud SQL). OpenHexa can be deployed on other cloud providers or in a private cloud, but you will need to adapt
the instructions below to your infrastructure of choice.

### Provisioning

In order to run the OpenHexa platform, you will need:

1. A Kubernetes cluster
1. A PostgreSQL server running PostgreSQL 11 or later

It is perfectly fine to run the OpenHexa **App** component in an existing Kubernetes cluster. All the Kubernetes
resources created for this component will be attached to a specific Kubernetes namespace named `hexa-app`.

#### Configure gcloud

We will need the [`gcloud`](https://cloud.google.com/sdk/gcloud) command-line tool for the next steps. Make sure it is
installed and configured properly - among other things, that the appropriate configuration is active.

The following command will show which configuration you are using:

```bash
gcloud config configurations list
```

#### Create a Cloud SQL instance

In the Google Cloud console, go to the Google Cloud SQL dashboard and create a new instance:

1. Choose **PostgreSQL** as the engine
1. Use `hexa-app` as the instance name
1. Choose a password for the root `postgres` account and keep it somewhere safe
1. Choose `PostgreSQL 12` as Postgres version
1. Choose an appropriate region
1. Customize the instance as needed (especially machine type and backups) and confirm the instance creation

Once the instance has been successfully created, you can create a database and a user:

1. Go to the **Databases** tab and create a new database called `hexa-app`
1. Go to the **Users** tab and create a new user called `hexa-app` (and save its credentials somewhere safe)

🚨 The created user will have root access on your instance. You should make sure to adapt its permissions accordingly if
needed.

The last step is to get the connection string of your Cloud SQL instance. Launch the following command and write down
the value next to the `connectionName` key, you will need it later:

```bash
gcloud sql instances describe hexa-app
```

#### Create a service account for the Cloud SQL proxy

The OpenHexa app component will connect to the Cloud SQL instance using a
[Cloud SQL Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy). The proxy requires a GCP service account. To
create it:

1. Go to the Service Accounts page of the GCP IAM & Admin section
1. Create a service account named `cloud-sql-proxy` and give it a description
1. Add the "Cloud SQL Client" permission to the service account
1. Confirm the service account description
1. Download a JSON credential files associated to the service account (Manage keys > Add Key > Create new key)
1. Keep it somewhere safe (don't version it, and delete the file once you don't need it anymore)

#### Create a GKE cluster:

In the Google Cloud console, go to the Google Kubernetes Engine dashboard and create a new cluster:

1. Choose Standard Mode
1. Name your cluster (`hexa-main` for example)
1. Choose the "Zonal" location type
1. Select the appropriate zone
1. In the "Default Pool" section, configure the default pool name and node configuration (we suggest to call it 
   `default-pool-<machine_type>`, where machine type refers to the GCP machine type that you will use for this pool - 
   for example, if you opt for the `n2-standard-2` machine type, you can name your pool `default-pool-n2s2`)
1. Choose a number of node and autoscaling settings (1 node as a starting point, 1-3 nodes with autoscaling enabled is 
   a sensible default)
1. Within the "Nodes" sub-section (under the "Default Pool" section), choose an appropriate machine type
1. Perform additional customization as needed and confirm the cluster creation

To make sure that the `kubectl` utility can access the newly created cluster, you need to launch another command:

```bash
gcloud container clusters get-credentials hexa-main --zone "<your_cluster-zone>"
```

### Deploying

The OpenHexa **App** component can be deployed with the `kubectl` utility. Almost all the required resources can be 
contained in a single file (we provide a sample `k8s/app.yaml` file to serve as a basis).

As we want all resources to be located in a specific Kubernetes namespace, create it if it does not exist yet:

```bash
kubectl create namespace hexa-app
```

Before we can deploy the app component, we need to create a secret for the Cloud SQL proxy:

```bash
kubectl create secret generic cloudsql-oauth-credentials -n hexa-app \
  --from-file=credentials.json=[PATH_TO_CREDENTIAL_FILE]
```

We need another secret for the Django environment variables:

```bash
kubectl create secret generic app-secret -n hexa-app \
  --from-literal DATABASE_USER=<DATABASE_USER> \
  --from-literal DATABASE_PASSWORD=<DATABASE_PASSWORD> \
  --from-literal DATABASE_NAME=<DATABASE_NAME> \
  --from-literal DATABASE_PORT=<DATABASE_PORT> \
  --from-literal SECRET_KEY=<SECRET_KEY>
```

Then, you can copy the sample file and adapt it to your needs:

```bash
cp k8s/app.yaml.dist k8s/app.yaml
nano k8s/app.yaml
```
You can then deploy the app component using `kubectl apply`:

```bash
kubectl apply -n hexa-app -f k8s/app.yaml
```

Don't forget to run the migrations (with fixtures if needed):

```bash
# Migrate
kubectl exec deploy/app-deployment -n hexa-app -- python manage.py migrate
# Load fixtures
kubectl exec deploy/app-deployment -n hexa-app -- python manage.py loaddata demo.json
```

If you need to run a command in a pod, you can use the following:

```bash
kubectl exec -it deploy/app-deployment -n hexa-app -- bash
```

Once the deployment is complete, you can get the public IP of the load balancer and access the app (or create a DNS 
record that points to it):

```bash
kubectl get service openhexa-app
```

Building the Docker image
-------------------------

The OpenHexa app Docker image is publicly available on Docker Hub
([blsq/openhexa-app](https://hub.docker.com/r/blsq/openhexa-app)).

This repository also provides a Github workflow to build the Docker image in the `.github/workflows` directory.

Local development
-----------------

In addition to the **App** component Docker image, we also provide a `docker-compose.yaml` file for local development.

The following steps will get you up and running:

```bash
docker-compose build
docker-compose run app fixtures
docker-compose up
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
docker-compose run app coverage

### Tailwind

OpenHexa uses [TailwindUI](https://tailwindui.com/) and [TailwindCSS](https://tailwindcss.com/) for the user interface. 
No specific step is required to use it, unless you want to perform changes to the TailwindUI/TailwindCSS configuration.

To be able to do that, you need to start tailwind in dev mode:

`docker-compose run app manage tailwind start`.
```

### Code style

Our python code is linted using [`black`](https://github.com/psf/black).

We use a [pre-commit](https://pre-commit.com/) hook to lint the code before committing. Make sure that `pre-commit` is
installed, and run `pre-commit install` the first time you check out the code.