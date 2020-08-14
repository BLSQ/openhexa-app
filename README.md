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
kubectl create namespace $NAMESPACE
```

### (Re-)build the single-user server image

We use a custom single-user server image, based on the 
[`jupyter/datascience-notebook`(https://hub.docker.com/r/jupyter/datascience-notebook/) image.

You will need to push it to an image repository, first when you set up Habari for the fist time, and then every time 
you make a change to the custom image.

To deploy the image, build, tag and push it:

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

Please note that using `latest` as tag might be problematic. If you encounter issues (such as new single-server nodes 
being created using a previous version of the image), using incremental values or commit hashes for tags might be a 
solution. We should consider automating this process.

### Create a GitHub OAuth application

As of now, Habari uses Github to authenticate its users. The setup is documented [here](https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html#github).

Please note that you will need to whitelist both admin and regular users using their Github usernames
(see the "Adapt the helm values file" section below).

### Create S3 buckets

In its present form, Habari uses two S3 buckets:

- A "Data lake" bucket to store data
- A "Notebooks" bucket for shared notebooks

You need to:

- Create the two buckets in S3
- Create a user with a policy that grants access to the S3 buckets
- Create an access key for the user, and note the associated `Access key ID` and `Secret access key`
  (you will need them later)

Example policy:

```json
{
    "Version": "2020-05-29",
    "Statement": [
        {
            "Sid": "AllAccess",
            "Action": "s3:*",
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::bucket-name-lake",
                "arn:aws:s3:::bucket-name-lake/*"
            ]
        },
        {
            "Sid": "AllAccess",
            "Action": "s3:*",
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::bucket-name-notebooks",
                "arn:aws:s3:::bucket-name-notebooks/*"
            ]
        }
    ]
}
```

### Adapt the helm values file

We will use a [Helm values file](https://helm.sh/docs/chart_template_guide/values_files/) to configure the deployment.

First, copy the `config.dist.yaml` file:

```bash
cp config.dist.yaml config.yaml
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
  --values config.yaml
```

### Uninstalling

Please note that that the ["Tearing Everything Down"](https://zero-to-jupyterhub.readthedocs.io/en/latest/setup-jupyterhub/turn-off.html) 
section of the Zero To Jupyterhub doc is not up-to-date for Helm 3. Give it a read to check the specificities for your 
cloud provider, but you will need to launch the following commands:

```bash
helm uninstall habari --namespace $NAMESPACE
kubectl delete namespace $NAMESPACE
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