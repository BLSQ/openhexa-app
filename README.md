Habari
======

Habari is a Data Science Platform developed by BlueSquare, based on the [Jupyter](https://jupyter.org/) ecosystem.

Architecture overview
---------------------

Right now, Habari is mostly just a (rather advanced) customised [JupyterHub](https://jupyter.org/hub) setup.

The mid-term objective is to embed this Jupyter setup in a web application. This work is in progress - see the 
[Platform section](#Platform) for more information.

The Jupyter part works as follows:

- A **Jupyterhub** instance is deployed within a Kubernetes cluster
- The hub spawns a **Kubernetes pod** for each single-user notebook server instance
- Single-user instances are connected to **S3** (data lake and shared notebooks)
- Single-user instances have access to a **PostgreSQL** database to facilitate external data access

### Kubernetes

Habari is meant to be deployed in a **Kubernetes cluster**. We use the official
[Zero to JupyterHub](https://zero-to-jupyterhub.readthedocs.io/) Jupyterhub distribution, which contains a Helm chart
that we will use to facilitate our deployments.

When the hub starts a single-user Jupyter notebook server, it actually spawns a new pod within the node pool. Each
single-user server instance is totally isolated from other instances.

Those single-user server instances use a customised Docker image based on the `datascience-notebook` image provided by
the [Jupyter Docker Stacks](https://github.com/jupyter/docker-stacks) project.

### Multi-tenancy

Multi-tenancy (multi-projects capabilities) in Habari is still a work in progress and will probably change in the
future. At the moment, we use **Kubernetes namespaces** to create distinct, project-specific deployments.

For each project, we create a new namespace, and deploy the Helm chart within the namespace with a specific
configuration.

### Data storage

In its present form, each project in Habari uses three **S3 buckets**:

- A **public** bucket for documentation, samples, public datasets (meant be shared across projects)
- A **lake** bucket for the project shared data
- A **notebooks** bucket for the project shared notebooks

The recommendation is to configure the public bucket to be read-only. An exception can be made for projects to which
only internal members of your organization have access: it can be useful to allow them to write to this bucket.

The data in the lake bucket can come from external processes / pipelines, but Habari users can also upload data to the
lake from the JupyterLab interface.

We also create a **PostgreSQL** database for each project. Users can access this database using pre-configured
environment variables. The main purpose of this database is to offer an easy way to expose data to other applications,
such as BI applications like Tableau or PowerBI.

Kubernetes setup
----------------

As recommended by the official JupyterHub documentation, we use Kubernetes to deploy the Habari Data platform.

Our setup is based on the [Zero To JupyterHub](https://zero-to-jupyterhub.readthedocs.io/) project and involves:

- A Kubernetes cluster
- A Helm chart
- Custom notebook server images

### Set up a Kubernetes cluster

**Note:** even if the Kubernetes cluster is already set up, you might have to give your account the permissions to
access it. Please check the documentation linked below.

The first step is to set up a Kubernetes cluster. The procedure for different cloud providers is explained
[in the JupyterHub documentation](https://zero-to-jupyterhub.readthedocs.io/en/latest/create-k8s-cluster.html) but is
not perfectly up-to-date, so you will need to refer to the cloud provided documentation.

What is important at this stage is that you end up with a properly configured Kubernetes cluster that you can access
using `kubectl`.

As an example, the easiest way to setup the cluster is to
use [Google Kubernetes Engine (GKE)](https://zero-to-jupyterhub.readthedocs.io/en/latest/google/step-zero-gcp.html).

### Set up Helm

We use Helm 3 for deployment, which is still in preview mode for Zero To JupyterHub but appears to work quite well.

It means that we don't need to configure Tiller. The Helm 3 setup is
explained [here](https://zero-to-jupyterhub.readthedocs.io/en/latest/setup-jupyterhub/setup-helm3.html).

Don't forget to add the JupyterHub helm chart repo:

```bash
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update
```

### About the single-user server image

The hub uses a custom single-user server image, based on the
[`jupyter/datascience-notebook`](https://hub.docker.com/r/jupyter/datascience-notebook/) image. This
[`blsq/habari-jupyter`](https://hub.docker.com/r/blsq/habari-jupyter) base image is available publicly on
[Dockerhub](https://hub.docker.com/r/blsq/habari-jupyter).

Note that we use incremental values for tags (`0.1`, `0.2` etc). It's safer to use those incremental tags in your
project config files rather than relying on the `latest` tag, as the image puller service does not always detect that a
new image has been published. It also prevents accidental deployments of new image versions.

The sample project config file uses this base image. You can, however, use any other image. Image can be specified on a
per-project basis (using the `singleuser.image` configuration as documented in the
[Zero To Jupyterhub documentation](https://zero-to-jupyterhub.readthedocs.io/en/latest/resources/reference.html#singleuser-image))
.

Creating a new project
----------------------

Now that you have a running cluster and the JupyterHub Helm chart, you can create a new project. The project will be
deployed in its own Kubernetes namespace.

### Add a Helm values file

We will use two [Helm values files](https://helm.sh/docs/chart_template_guide/values_files/) when deploying:

1. The base `shared_config.yaml` file, containing config values shared across projects
1. A project-specific file

You will use both files when deploying the project using `helm`.

Feel free to organize project config files as you see fit. Be careful about version control: those project-specific file
typically contain sensitive data (such as database or s3 credentials). You can either ignore the files in version
control, encrypt them (using [sops](https://github.com/mozilla/sops) for example), or handle those config files in a
secure fashion in your continuous deployment infrastructure.

To create a new project, simply copy the `sample_project_config.yaml`:

```bash
cd jupyter
cp sample_project_config.yaml path_to_project_config.yaml
```

You can already fill some of the values within the files. You will set other values while going through the installation
steps below.

The sample file is commented with links to the relevant parts of the Zero To JupyterHub documentation. Most of the edits
you need to make are straightforward.

### Create a GitHub OAuth application

As of now, Habari uses Github to authenticate its users. The setup is documented
[here](https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html#github).

For the `Authorization callback URL` parameter, use `https://your-habari-workspace-address/hub/oauth_callback`.

Please note that you will need to whitelist both admin and regular users using their Github usernames in your project
config (see the "Add a Helm values file" section below).

Update the Helm values file with the application client id and secret (in `auth.github`).

### Create the S3 buckets and associated user

For each project, you need to:

- Create the "lake" and "notebooks" buckets in S3, and note their names somewhere
- If you haven't done it already, create the "public" bucket
- Create a user and attach an inline policy that grants access to the S3 buckets
- Create an access key for the user, and note the associated `Access key ID` and `Secret access key`
  (you will need them later)

Example policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3HabariPublicBucketNameRead",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::public-bucket-name",
        "arn:aws:s3:::public-bucket-name/*"
      ]
    },
    {
      "Sid": "S3HabariPublicBucketNameWriteKeepFile",
      "Action": [
        "s3:*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::public-bucket-name/.s3keep"
      ]
    },
    {
      "Sid": "S3HabariLakeBucketName",
      "Action": "s3:*",
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::lake-bucket-name",
        "arn:aws:s3:::lake-bucket-name/*"
      ]
    },
    {
      "Sid": "S3HabariNotebookBucketName",
      "Action": "s3:*",
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::notebooks-bucket-name",
        "arn:aws:s3:::notebooks-bucket-name/*"
      ]
    }
  ]
}
```

Update the Helm values file with the user credentials (in `singleuser.extraEnv` - `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY`).

### Create the project databases

Each Habari project uses two PostgreSQL databases:

1. The "hub" database, used as an admin database for Jupyterhub itself (instead of the default SQLite database)
1. The "explore" database, intended as a storage for user-generated data

Create the two databases and the associated users (don't use the same PostgreSQL users across projects, especially for
the explore database: its credentials are exposed to the end users).

Update the Helm values file with the database user credentials (in `hub.db.url` for the hub database, and in
`singleuser.extraEnv` for the explore database - check the `EXPLORE_DB_` environment variables.

### Deploy

You can then deploy using `helm`:

```bash
helm upgrade --install "habari-<project_name>" jupyterhub/jupyterhub \
  --namespace "<project_name>" \
  --create-namespace \
  --version=0.9.0 \
  --values shared_config.yaml \
  --values path_to_project_config.yaml
```

Updating and redeploying an existing project
--------------------------------------------

Redeploying a project is a simple process:

1. If needed, update the jupyter image used by the project
1. Adapt the project-specific value files if appropriate (don't forget to change `singleuser.image.tag` if your jupyter
   image has changed)
1. Re-deploy using `helm`

The deploy command is the same as the one we used when creating the project:

```bash
cd jupyter
helm upgrade --install "habari-<project_name>" jupyterhub/jupyterhub \
  --namespace "<project_name>" \
  --version=0.9.0 \
  --values shared_config.yaml \
  --values path_to_project_config.yaml
```

Uninstalling
------------

Please note that that
the ["Tearing Everything Down"](https://zero-to-jupyterhub.readthedocs.io/en/latest/setup-jupyterhub/turn-off.html)
section of the Zero To Jupyterhub doc is not up-to-date for Helm 3. Give it a read to check the specifics for your cloud
provider.

You can use `helm` and `kubectl` to delete the Helm release and the Kubernetes namespace:

```bash
helm uninstall "habari-<project_name>" --namespace "<project_name>"
kubectl delete namespace <project_name>
```

Local setup
-----------

When developing / testing locally, you have two options:

1. Launching Jupyter only (without the hub) using `docker-compose` - this might be ideal when developing Jupyter
   extensions or Jupyter-specific code
1. Launching Habari in a local Kubernetes cluster - this is the best option if you want a local setup close to the
   production one

### Jupyter-only with docker-compose

First, create the S3 buckets, the IAM user and the associated policy. You can use the same instructions as for the cloud
setup described above.

You can then enter the `jupyter` directory and copy the `.env` file:

```bash
cd jupyter
cp .env.dist .env
```

Adapt the copied file to your needs using the AWS credentials created earlier.

Build the Docker images and launch:

```bash
docker-compose build
docker-compose up
```

The platform will be available at http://localhost:8000/.

### Local Kubernetes cluster

First, create the Github Oauth app, the S3 buckets, the IAM user and the associated policy. You can use the same
instructions as for the cloud setup described above.

Then, make sure that you current Kubernetes context is correct: `kubectl config current-context` should return the name
of your local cluster.

For your convenience, we provide a `docker-compose.postgres.yaml` file to provision locally the different Postgres
instances:

```bash
cd jupyter
docker-compose -f docker-compose.postgres.yaml up
```

You can then follow the same instructions as the ones provided for the cloud setup above, keeping in mind that:

- The `proxy.https` part can be commented, as it will be challenging to make it work locally
- The Github Oauth system won't work with localhost - you will have to use something like
  [ngrok](https://ngrok.com/), and use the provided IP address in the Oauth app setting and in your project config file
- The Kubernetes pods won't be able to connect to the database through localhost, you will need to use an IP
  (if you use Docker Desktop on Mac, `host.docker.internal` will do the trick)

Troubleshooting
---------------

### My hub is configured with letsencrypt but is not accessible through tls/https

It might be an issue with the `autohttps` service. A possible solution is to delete the `autohttps` pod in your project
namespace and redeploy.

Platform
--------

🚧 This part of the platform is very WIP

What we mean by platform is a web application, in which the Jupyter component described above will be embedded.

As of now, the platform is a simple Django application connected to a PostgreSQL database. A `docker-compose` file
allows run to develop and test it locally.

The UX relies on TailwindCSS (& TailwindUI), through [django-tailwind](https://github.com/timonweb/django-tailwind).

A [`blsq/habari-platform`](https://hub.docker.com/r/blsq/habari-platform) Docker image is published on Docker hub for
your convenience.

### Local development

Build and Launch with:

```bash
docker-compose build
docker-compose up
```

In another terminal, launch the migrations, create a superuser and load the catalog fixtures:

```bash
docker-compose run app python manage.py migrate
docker-compose run -e DJANGO_SUPERUSER_PASSWORD=root -e DJANGO_SUPERUSER_USERNAME=root -e DJANGO_SUPERUSER_EMAIL=foo@bar.com app python manage.py createsuperuser --no-input
docker-compose run app python manage.py loaddata habari/catalog/fixtures/demo.json
```

If you want to perform TailwindUI/TailwindCSS optimizations or update, you need to start tailwind in dev mode:

`docker-compose run app python manage.py tailwind start`.

### Deploying

This Django application can be deployed on any server that supports Python. The `k8s` directory contains a sample
Kubernetes deployment config.

The platform docker image can be built using the "Build Platform image" Github workflow.

Don't forget to build the production stylesheet before rebuilding your image:

`docker-compose run web python manage.py tailwind build`.

### Building the image

We build the platform image using the following commands:

```bash
docker build -t habari-platform .
docker tag habari-platform:latest habari-platform:x.y.z
docker tag habari-platform:latest blsq/habari-platform:latest
docker tag habari-platform:x.y.z blsq/habari-platform:x.y.z
docker push blsq/habari-platform:latest
docker push blsq/habari-platform:x.y.z
```