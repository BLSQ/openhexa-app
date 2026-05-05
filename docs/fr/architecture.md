<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Architecture technique</h1>
</div>
</div>

OpenHEXA est une plateforme d'intégration de données composée d'une série de composants :

- L'**application OpenHEXA**, généralement appelée [`openhexa-app`](https://github.com/BLSQ/openhexa-app) pour des raisons historiques, une application Python/Django fournissant une API GraphQL, un moteur d'orchestration de pipelines de données, des fonctionnalités de gestion des utilisateurs et un frontend NextJS
- L'environnement **OpenHEXA notebooks** (voir [`openhexa-notebooks`](https://github.com/BLSQ/openhexa-notebooks)), une configuration JupyterHub/JupyterLab fortement personnalisée exécutant la même image que l'environnement des pipelines

En matière de stockage de données, il faut faire une distinction entre :

- Le **stockage des données de l'application**, qui réside dans une base de données PostgreSQL
- Le **stockage de l'espace de travail** ou _stockage utilisateur_ (voir le [Manuel d'utilisation](workspaces.md) pour plus d'informations sur les espaces de travail), qui est stocké soit dans des bases de données PostgreSQL, soit dans des buckets de stockage objet (Google Cloud Storage, AWS S3 ou Minio)

Lors de l'exécution de code via les notebooks Jupyter ou les pipelines de données OpenHEXA, les utilisateurs techniques peuvent tirer parti du **SDK Python OpenHEXA** pour interagir avec le backend OpenHEXA (voir [`openhexa-sdk-python`](https://github.com/BLSQ/openhexa-sdk-python)).

Les notebooks et les pipelines de données s'exécutent généralement dans des conteneurs utilisant l'une de nos images Docker (voir [`openhexa-docker-images`](https://github.com/BLSQ/openhexa-docker-images)) ou une image personnalisée définie par espace de travail.

L'ensemble de la pile OpenHEXA est destiné à être déployé dans un **cluster Kubernetes**, afin que les notebooks et les pipelines s'exécutent dans des environnements isolés et bénéficient des capacités d'auto-scaling offertes par Kubernetes.

![architecture](https://github.com/BLSQ/openhexa/assets/1607549/6d3d4c79-7610-40d8-9d14-4d2ca62102d1)
