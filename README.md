<div align="center">
   <img alt="OpenHexa Logo" src="https://openhexa.bluesquare.org/static/img/logo/logo_with_text_black.svg" height="80">
</div>

OpenHexa App Component
======================

OpenHexa is an **open-source data integration platform** that allows users to:

- Explore data coming from a variety of sources in a **data catalog**
- Schedule **data pipelines** for extraction & transformation operations
- Perform data analysis in **notebooks**
- Create rich data **visualizations**

<div align="center">
   <img alt="OpenHexa Screenshot" src="https://openhexa.bluesquare.org/static/img/screenshots/datasource_detail.png" hspace="10" height="150">
   <img alt="OpenHexa Screenshot" src="https://openhexa.bluesquare.org/static/img/screenshots/notebooks.png" hspace="10" height="150">
</div>

OpenHexa architecture
---------------------

The OpenHexa platform is composed of **three main components**:

- The **App component**, a Django application that acts as the user-facing part of the OpenHexa platform
- The **Notebooks component** (a [JupyterHub](https://jupyter.org/hub) setup)
- The **Data Pipelines component** (build on top of [Airflow](https://airflow.apache.org/))

This repository contains the code for the **App component**, which servers as the user-facing part of the OpenHexa
stack.

The code related to the Notebooks component can be found in the
[`openhexa-notebooks`](https://github.com/blsq/openhexa-notebooks) repository, while the Data Pipelines component 
code resides in the [`openhexa-pipelines`](https://github.com/blsq/openhexa-pipelines) repository.

App component overview
----------------------

The **App component** is a [Django](https://www.djangoproject.com/) application connected to a
[PostgreSQL](https://www.postgresql.org/) database.

This component is meant to be deployed in a [Kubernetes](https://kubernetes.io/) cluster (either in a public cloud or in
your own infrastructure).

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

Provisioning
------------

**Note:** the following instructions are tailored to a Google Cloud Platform setup (using Google Kubernetes Engine and
Google Cloud SQL). OpenHexa can be deployed on other cloud providers or in a private cloud, but you will need to adapt
the instructions below to your infrastructure of choice.

### Requirements

In order to run the OpenHexa **App component**, you will need:

1. A **Kubernetes cluster**
1. A **PostgreSQL server** running PostgreSQL 11 or later

It is perfectly fine to run the OpenHexa **App component** in an existing Kubernetes cluster. All the Kubernetes
resources created for this component will be attached to a specific Kubernetes namespace named `hexa-app`.

#### Configure gcloud

We will need the [`gcloud`](https://cloud.google.com/sdk/gcloud) command-line tool for the next steps. Make sure it is
installed and configured properly - among other things, that the appropriate configuration is active.

The following command will show which configuration you are using:

```bash
gcloud config configurations list
```

#### Create a global IP address (and a DNS record)

The Kubernetes ingress used to access the OpenHexa app component exposes an external IP. This IP might change when 
re-deploying or re-provisioning. In order to prevent it, create an address in GCP compute and get back its value:

```bash
gcloud compute addresses create <HEXA_APP_ADDRESS_NAME> --global
gcloud compute addresses describe <HEXA_APP_ADDRESS_NAME> --global
```

Then, you can create a DNS record that points to the ip address returned by the `describe` command above.

#### Create a Cloud SQL instance, database and user

Unless you already have a ready-to-use Google Cloud SQL instance, you can create one using the following command:

```bash
gcloud sql instances create hexa-main \
 --database-version=POSTGRES_12 \
 --cpu=2 --memory=7680MiB --zone=europe-west1-b --root-password=asecurepassword
```

You will then need to create a database for the App component:

```bash
gcloud sql databases create hexa-app --instance=hexa-main
```

You will need a user as well:

```bash
gcloud sql users create hexa-app --instance=hexa-main --password=asecurepassword
```

🚨 The created user will have root access on your instance. You should make sure to adapt its permissions accordingly if
needed.

The last step is to get the connection string of your Cloud SQL instance. Launch the following command and write down
the value next to the `connectionName` key, you will need it later:

```bash
gcloud sql instances describe hexa-main
```

#### Create a service account for the Cloud SQL proxy

The OpenHexa app component will connect to the Cloud SQL instance using a
[Cloud SQL Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy). The proxy requires a GCP service account. If 
you have not created such a service account yet, create one:

```bash
gcloud iam service-accounts create hexa-cloud-sql-proxy \
  --display-name=hexa-cloud-sql-proxy \
  --description='Used to allow pods to access Cloud SQL'
```

Give it the `roles/cloudsql.client` role:

```bash
gcloud projects add-iam-policy-binding blsq-dip-test \
    --member=serviceAccount:hexa-cloud-sql-proxy@blsq-dip-test.iam.gserviceaccount.com \
    --role=roles/cloudsql.client
```

Finally, download a key file for the service account and keep it somewhere safe, we will need it later:

```bash
mkdir -p ../gcp_keyfiles
gcloud iam service-accounts keys create ../gcp_keyfiles/hexa-cloud-sql-proxy.json \
  --iam-account=hexa-cloud-sql-proxy@blsq-dip-test.iam.gserviceaccount.com
```

Note that we deliberately download the key file outside the current repository to avoid it being included 
in Git or in the Docker image.

#### Create a GKE cluster:

Unless you already have a running Kubernetes cluster, you need to create one. The following command 
will create a new cluster in Google Kubernetes Engine, along with a default node pool:

```bash
gcloud container clusters create hexa-main \
  --machine-type=n2-standard-2 \
  --zone=europe-west1-b \
  --enable-autoscaling \
  --num-nodes=1 \
  --min-nodes=1 \
  --max-nodes=4 \
  --cluster-version=latest
```

The `node-labels` and `node-taints` options will allow JupyterHub to spawn the single-user Jupyter server pods in the 
user node pool.

To make sure that the `kubectl` utility can access the newly created cluster, you need to launch another command:

```bash
gcloud container clusters get-credentials hexa-main --region=europe-west1-b
```

Deploying
---------

The OpenHexa **App component** can be deployed with the `kubectl` utility. Almost all the required resources can be
contained in a single file (we provide a sample `k8s/sample_app.yaml` file to serve as a basis).

As we want all resources to be located in a specific Kubernetes namespace, create it if it does not exist yet:

```bash
kubectl create namespace hexa-app
```

Before we can deploy the app component, we need to create a secret for the Cloud SQL proxy:

```bash
kubectl create secret generic hexa-cloudsql-oauth-credentials -n hexa-app \
  --from-file=credentials.json=../gcp_keyfiles/hexa-cloud-sql-proxy.json
```

We need another secret for the Django environment variables. First, you need to generate a secret key for the 
Django application:

```bash
docker-compose run app manage generate_secret_key
```

Then, create the secret:

```bash
kubectl create secret generic app-secret -n hexa-app \
  --from-literal DATABASE_USER=<HEXA_APP_DATABASE_USER> \
  --from-literal DATABASE_PASSWORD=<HEXA_APP_DATABASE_PASSWORD> \
  --from-literal DATABASE_NAME=<HEXA_APP_DATABASE_NAME> \
  --from-literal SECRET_KEY=<HEXA_APP_SECRET_KEY>
```

Then, you can copy the sample file and adapt it to your needs:

```bash
cp k8s/sample_app.yaml k8s/app.yaml
nano k8s/app.yaml
```

A few notes about the sample file:

1. `HEXA_APP_DOMAIN` should be replaced by the value of the DNS record that points to your OpenHexa app instance
   (`openhexa.yourorg.com` for example)
1. `HEXA_APP_NODE_POOL_SELECTOR` should be set to the name of the node pool that will run your OpenHexa app pods
   (example: `default-pool`)
1. `HEXA_APP_IMAGE` is the full path of the OpenHexa app image (`blsq/openhexa-app:latest` or `blsq/openhexa-app:0.3.1`,
   or a path to a custom image)1
1. `HEXA_CLOUDSQL_CONNECTION_STRING` corresponds to the `connectionName` value returned by the 
   `gcloud sql instances describe` command (see above)
1. `HEXA_APP_ADDRESS_NAME` is the named used when creating the address using the `gcloud compute addresses create` command
1. `HEXA_NOTEBOOKS_URL` should be replaced by the URL of the DNS record that points to your OpenHexa notebooks
   instance (`https://notebooks.openhexa.yourorg.com` for example)

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

Once the deployment is complete, you can get the public IP of the load balancer and create a DNS record that points
to it:

```bash
kubectl get service app-service -n hexa-app
```

Building the Docker image
-------------------------

The OpenHexa app Docker image is publicly available on Docker Hub
([blsq/openhexa-app](https://hub.docker.com/r/blsq/openhexa-app)).

This repository also provides a Github workflow to build the Docker image in the `.github/workflows` directory.

Provision and deploy the Notebooks component
--------------------------------------------

The app component will embed the [Notebooks component](https://github.com/blsq/openhexa-notebooks) as an `iframe` in a 
dedicated section.

Before deploying the App component, you will need to deploy the Notebooks component, following the instructions 
provided in the [`README.md`](https://github.com/blsq/openhexa-notebooks/blob/main/README.md) of the Notebooks 
component.

It's important to have the Notebooks and App components running on the same top-level domain, as we use cookies for 
cross-component authentication.

Local development
-----------------

In addition to the **App component** Docker image, we also provide a `docker-compose.yaml` file for local development.

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

To be able to do that, you need to install `django-tailwind` and start tailwind in dev mode:

`docker-compose run app manage tailwind install`.
`docker-compose run app manage tailwind start`.
```

### Code style

Our python code is linted using [`black`](https://github.com/psf/black).

We use a [pre-commit](https://pre-commit.com/) hook to lint the code before committing. Make sure that `pre-commit` is
installed, and run `pre-commit install` the first time you check out the code.