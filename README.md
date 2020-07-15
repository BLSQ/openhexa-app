Habari
======

Habari is a Data Science Platform developed by BlueSquare.

The platform is based on the following technologies:

- Jupyter (https://jupyter.org/)
- JupyterHub (https://jupyter.org/hub)

Kubernetes setup
----------------

As recommended by the official JupyterHub documentation, we use Kubernetes to deploy the Habari Data platform.

Our setup is based on the [Zero To JupyterHub](https://zero-to-jupyterhub.readthedocs.io/) project and involves:

- A Kubernetes cluster
- Helm deployments
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

You will also need to create (at least) one namespace:

```bash
NAMESPACE=your_namespace
kubectl create $NAMESPACE 
```

### Deploy

First, copy the `config.dist.yaml` file:

```bash
cp config.dist.yaml config.yaml
```

Edit the file to fit your needs. The sample file provides is commented with links to the relevant parts of the 
Zero To JupyterHub documentation.

You can then deploy using the following command:

```bash
helm upgrade --install habari jupyterhub/jupyterhub \
  --namespace $NAMESPACE \
  --version=0.9.0 \
  --values config.yaml
  --set singleuser.image.tag=some_tag
```

### Updating the single-user server image

We use a custom single-user server image, based on the 
[`jupyter/datascience-notebook`(https://hub.docker.com/r/jupyter/datascience-notebook/) image.

To deploy and updated version, you need to build, tag and push the jupyter image:

```bash
docker build -t habari-jupyter:latest jupyter
docker tag habari-jupyter:latest your.image.registry/full-image-name:latest
docker push your.image.registry/full-image-name:tag1
```

As an example, if you use the GCP platform:

```bash
GCP_PROJECT_ID=your-gcp-project-id

docker build -t habari-jupyter:latest jupyter
docker tag habari-jupyter:latest eu.gcr.io/$GCP_PROJECT_ID/habari-jupyter:latest
docker push eu.gcr.io/$GCP_PROJECT_ID/habari-jupyter:latest
```


### Multi-tenancy

Multi-tenancy for Habari has not been completely figured out yet.

At this point, the likely scenario would be to:

- Create one Kubernetes namespace per tenant
- Deploy the habari release into each namespace using different config values

A simple way to handle different config values would be to have one `config.yaml` file per tenant, but we need 
to figure out a place those store these configuration files in a secure fashion.

Another possibility would be to handle that at the CI/CD level.

Local setup
-----------

(TBC, out of date)

Habari provides a docker-based environment, useful for a local development environment.

To launch it, just build the image and up:

```bash
docker-compose build
docker-compose up
```

The platform will be available at http://localhost:8000/.

You will then need to:

1. Create a user account using the `habari` username and a password of your choice (
   the signup is available at http://localhost:8000/hub/signup)
2. Log in with this account (http://localhost:8000/hub/login)

This account will be the first admin account, that you can use in turn to create other users.