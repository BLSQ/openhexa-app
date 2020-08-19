Habari
======

Habari is a Data Science Platform developed by BlueSquare, based on the [Jupyter](https://jupyter.org/) ecosystem.

Architecture overview
---------------------

Right now, Habari is just a (rather advanced) customised [JupyterHub](https://jupyter.org/hub) setup:

- A **Jupyterhub** instance running on Kubernetes
- The hub spawns a **Kubernetes pod** for each single-user notebook server instance
- Single-user instances are connected to **S3 or GCS buckets** (data lake and shared notebooks)
- Single-user instances have access to a **PostgreSQL** database to facilitate external data access

The longer-term goal is to transform Habari into a broader application, with this JupyterHub setup as one of its 
components.

### Kubernetes

Habari is meant to be deployed in a **Kubernetes cluster**. We use the official 
[Zero to JupyterHub](https://zero-to-jupyterhub.readthedocs.io/) Jupyterhub distribution, which contains a Helm chart 
that we will use to facilitate our deployments.

When the hub starts a single-user Jupyter notebook server, it actually spawns a new pod within the node pool. 
Each single-user server instance is totally isolated from other instances.

Those single-user server instances use a customised Docker image based on the `datascience-notebook` image provided 
by the [Jupyter Docker Stacks](https://github.com/jupyter/docker-stacks) project.


### Multi-tenancy

Multi-tenancy (multi-projects capabilities) in Habari is still a work in progress and will probably change in the 
future. At the moment, we use **Kubernetes namespaces** to create distinct, project-specific deployments.

For each project, we create a new namespace, and deploy the Helm chart within the namespace with a specific 
configuration.

Creating the project and its resources is currently a manual process.

### Data storage

In its present form, each project in Habari uses two **S3 buckets**:

- A **lake** bucket for shared data
- A **notebooks** bucket for shared notebooks

The data in the lake bucket can come from external processes / pipelines, but Habari users can also upload data 
to the lake from the JupyterLab interface.

We also create a **PostgreSQL** database for each project. Users can access this database using pre-configured environment 
variables. The main purpose of this database is to offer an easy way to expose data to other applications, such as BI 
applications like Tableau or PowerBI.

Kubernetes setup
----------------

As recommended by the official JupyterHub documentation, we use Kubernetes to deploy the Habari Data platform.

Our setup is based on the [Zero To JupyterHub](https://zero-to-jupyterhub.readthedocs.io/) project and involves:

- A Kubernetes cluster
- A Helm chart
- Custom notebook server images

### Set up a Kubernetes cluster

The first step is to set up a Kubernetes cluster. The procedure for different cloud providers is explained 
[in the JupyterHub documentation](https://zero-to-jupyterhub.readthedocs.io/en/latest/create-k8s-cluster.html) but is 
not perfectly up-to-date, so you will need to refer to the cloud provided documentation.

What is important at this stage is that you end up with a properly configured Kubernetes cluster that you can access 
using `kubectl`.

As an example, the easiest way to setup the cluster is to use [Google Kubernetes Engine (GKE)](https://zero-to-jupyterhub.readthedocs.io/en/latest/google/step-zero-gcp.html).

### Set up Helm

We use Helm 3 for deployment, which is still in preview mode for Zero To JupyterHub but appears to work quite well.

It means that we don't need to configure Tiller. The Helm 3 setup is explained [here](https://zero-to-jupyterhub.readthedocs.io/en/latest/setup-jupyterhub/setup-helm3.html). 

Don't forget to add the JupyterHub helm chart repo:

```bash
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update
```

### (Re-)build the single-user server image

The hub uses a custom single-user server image, based on the 
[`jupyter/datascience-notebook`](https://hub.docker.com/r/jupyter/datascience-notebook/) image.

You will need to push it to an image repository, first when you set up Habari for the fist time, and then every time 
you make a change to the custom image.

```bash
docker build -t habari-jupyter:latest jupyter
docker tag habari-jupyter:latest your.image.registry/full-image-path:latest
docker tag habari-jupyter:latest your.image.registry/full-image-path:x.x
docker push your.image.registry/full-image-path:latest
docker push your.image.registry/full-image-path:x.x
```

As an example, if you use the GCP platform:

```bash
GCP_PROJECT_ID=your-gcp-project-id
docker build -t habari-jupyter:latest jupyter
docker tag habari-jupyter:latest eu.gcr.io/$GCP_PROJECT_ID/habari-jupyter:latest
docker tag habari-jupyter:latest eu.gcr.io/$GCP_PROJECT_ID/habari-jupyter:x.x
docker push eu.gcr.io/$GCP_PROJECT_ID/habari-jupyter:latest
docker push eu.gcr.io/$GCP_PROJECT_ID/habari-jupyter:x.x
```

We currently use the same image for our different projects, but we could also consider using project-specific images in 
the future.

Creating a new project
----------------------

Now that you have a running cluster and the JupyterHub Helm chart, you can create a new project.

### Create a new Kubernetes namespace

The first step is to create a new namespace:

```bash
NAMESPACE=your_namespace
kubectl create namespace $NAMESPACE
```

We will deploy the Helm chart within this namespace.

### Create a GitHub OAuth application

As of now, Habari uses Github to authenticate its users. The setup is documented 
[here](https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html#github).

Please note that you will need to whitelist both admin and regular users using their Github usernames in your project 
config (see the "Add a helm values file" section below).

### Create the S3 buckets

For each project, you need to:

- Create the "lake" and "notebooks" buckets in S3
- Create a user with a policy that grants access to the S3 buckets
- Create an access key for the user, and note the associated `Access key ID` and `Secret access key`
  (you will need them later)

Example policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3HabariLakeBucketNameAccess",
            "Action": "s3:*",
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::lake-bucket-name",
                "arn:aws:s3:::lake-bucket-name/*"
            ]
        },
        {
            "Sid": "S3HabariNotebookBucketNameAccess",
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

### Create the project databases

Each Habari project uses two PostgreSQL databases:

1. The "hub" database, used as an admin database for Jupyterhub itself (instead of the default SQLite database)
1. The "explore" database, intended as a storage for user-generated data

### Add a helm values file

We will use two [Helm values files](https://helm.sh/docs/chart_template_guide/values_files/) when deploying:

1. The base `config.yaml` file, containing config values shared across projects
1. A project-specific file

Project-specific value files reside in the `config` directory. The content of this directory is ignored in git, except 
for the `sample-project.dist.yaml` example file.

To create a new project, simply copy the `sample-project.dist.yaml`:

```bash
cp config/sample-project.dist.yaml config/project-name.yaml
```

Edit the file to fit your needs. The sample file is commented with links to the relevant parts of the 
Zero To JupyterHub documentation. Most of the edits you need to make are straightforward.

The `singleuser.image` section can be a bit tricky. Here is an example for images hosted on GCR:

```yaml
singleuser:
  image:
    name: eu.gcr.io/<gcp-project-id>/habari-jupyter
    tag:  latest
    pullSecrets:
      - gcr-pull
```

### Deploy

You can then deploy using the following command:

```bash
helm upgrade --install habari jupyterhub/jupyterhub \
  --namespace $NAMESPACE \
  --version=0.9.0 \
  --values config.yaml \
  --values config/project-name.yaml
```

Note that we use the two value files mentioned above: the shared file as well as the project-specific file.

### Uninstalling

Please note that that the ["Tearing Everything Down"](https://zero-to-jupyterhub.readthedocs.io/en/latest/setup-jupyterhub/turn-off.html) 
section of the Zero To Jupyterhub doc is not up-to-date for Helm 3. Give it a read to check the specificities for your 
cloud provider, but you will need to launch the following commands:

```bash
helm uninstall habari --namespace $NAMESPACE
kubectl delete namespace $NAMESPACE
```

Re-deploying a project
----------------------

Redeploying a project is a simple process:

1. If needed, rebuild, tag and push the single-server Docker image to your image registry as explained above
1. Adapt the project-specific value files if appropriate (if you have built and tagged a new image in step 1, 
   don't forget to change it under `singleuser.image.tag`)
1. Re-deploy using `helm upgrade`

The Helm command is similar to the one we used when we created the project:

```bash
helm upgrade habari jupyterhub/jupyterhub \
  --namespace $NAMESPACE \
  --version=0.9.0 \
  --values config.yaml \
  --values config/project-name.yaml
```

Local setup
-----------

This setup is very different from the Kubernetes setup described above. We could consider using a local Kubernetes 
cluster for testing / experimenting with the platform as well.

The following steps should allow you to test parts of the platform on your local machine:

### Create a GitHub OAuth application and the two S3 buckets

Same instructions as for the Kubernetes setup described above.

### Copy and adapt env file

```bash
cp .env.dist .env
```

Adapt the copied file to your needs, using the Github / AWS credentials created earlier.

You also need to set `PROJECT_PATH` to the absolute path of the project directory on your machine.

### Build and launch

```bash
docker-compose build
docker-compose up
```

The platform will be available at http://localhost:8000/.

Note: you can also launch the jupyter single-user server alone (without the hub) by using the 
`docker-compose.nohub.yml` instead of the regular compose file. This is particularly useful when working locally on 
customisations of the single-user server.