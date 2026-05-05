<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Technical Architecture</h1>
</div>
</div>

OpenHEXA is a data integration platform composed of a series of components:

- The **OpenHEXA application**, usually called [`openhexa-app`](https://github.com/BLSQ/openhexa-app) for historical reasons, a Python/Django application providing a GraphQL API, a data pipelines' orchestration engine, user management capabilities and a NextJS frontend 
- The **OpenHEXA notebooks** environment (see [`openhexa-notebooks`](https://github.com/BLSQ/openhexa-notebooks)), a heavily customized JupyterHub/JupyterLab setup running the same image as the pipelines environment

In terms of data storage, we have to make a distinction between:

- **Application data storage**, which resides in a PostgreSQL database
- **Workspace storage** or _user storage_ (see [User manual](workspaces.md) for more information about workspaces), which is stored either in PosgtreSQL databases or in Object Storage buckets (Google Cloud Storage, AWS S3 or Minio)

When running code using Jupyter notebooks or OpenHEXA data pipelines, technical users can leverage the **OpenHEXA Python SDK** to interact with the OpenHEXA backend (see [`openhexa-sdk-python`](https://github.com/BLSQ/openhexa-sdk-python)).

Notebooks and data pipelines typically run in containers using one of our Docker images (see [`openhexa-docker-images`](https://github.com/BLSQ/openhexa-docker-images)) or a custom one set by workspace.

The whole OpenHEXA stack is meant to be deployed in a **Kubernetes cluster**, so that notebooks and pipelines run in isolated environments and leverage the auto-scaling capabilities offered by Kubernetes.

![architecture](https://github.com/BLSQ/openhexa/assets/1607549/6d3d4c79-7610-40d8-9d14-4d2ca62102d1)


