<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Instructions d'installation</h1>
</div>
</div>

La plateforme OpenHEXA est composée de plusieurs composants, chacun ayant son propre dépôt :

- [BLSQ/openhexa-app](https://github.com/BLSQ/openhexa-app) : le **composant App** (application Django pour la logique métier et l'API)
- [BLSQ/openhexa-frontend](https://github.com/BLSQ/openhexa-app/tree/main/frontend) : le **composant Frontend**, une application React/NextJS
- [BLSQ/openhexa-notebooks](https://github.com/BLSQ/openhexa-notebooks) : le **composant Notebooks**, une configuration personnalisée de [JupyterHub](https://jupyter.org/hub)

La méthode recommandée pour déployer OpenHEXA est d'utiliser [Kubernetes](http://kubernetes.io/). Pour une installation de développement local, nous recommandons d'utiliser Docker.

## Installation pour le développement

Comme chaque composant nécessite une pile différente, pour le développement local, nous recommandons d'utiliser Docker. Nous fournissons des manifestes Docker Compose pour déployer les apps OpenHEXA et les Notebooks. Quant au frontend, il nécessite un environnement Node local pour être exécuté directement.

En bref, lorsque les 3 dépôts Git des composants ont été clonés localement, vous pouvez les exécuter dans cet ordre :

1. l'app avec le runner et le scheduler de pipelines,
2. le notebook, puis
3. le frontend.

Vous trouverez les instructions détaillées pour le développement local dans le README de chaque composant :

* [app](https://github.com/BLSQ/openhexa-app/blob/main/README.md#local-development),
* [frontend](https://github.com/BLSQ/openhexa-frontend#local-development), et
* [notebook](https://github.com/BLSQ/openhexa-notebooks#local-development).

Même si le composant est conteneurisé, les modifications de votre copie de travail locale seront prises en compte.

Ci-dessous, vous trouverez une version courte pour configurer rapidement un environnement de développement pour OpenHEXA :

## Prérequis

* [Docker Engine](https://docs.docker.com/engine/install/)
* [Node.js Version Manager](https://github.com/nvm-sh/nvm#install--update-script)

## App

```bash
git clone git@github.com:BLSQ/openhexa-app.git
cp .env.dist .env
# editez le fichier .env pour configurer votre instance
docker network create openhexa
docker compose build
docker compose run app fixtures
docker compose --profile pipelines up
```

Deux points de terminaison URL sont maintenant exposés localement sur le port `8000` :

* `http://localhost:8000/graphql` pour l'API GraphQL
* `http://localhost:8000/ready` pour le point de terminaison de readiness

## Notebooks

```bash
git clone git@github.com:BLSQ/openhexa-notebooks.git
docker compose -f docker-compose.yml -f docker-compose-withdockerhub.yml up
```

## Frontend

```bash
git clone git@github.com:BLSQ/openhexa-frontend.git
npm install
cp .env.local.dist .env.local
# editez le fichier .env pour configurer votre instance
npm run dev
```

L'application web est alors servie localement sur le port `3000`. Vous pouvez naviguer et vous connecter à `http://localhost:3000`. Les identifiants par défaut sont
`root@openhexa.org`/`root`.

## Déploiement d'OpenHEXA

[Kubernetes](https://kubernetes.io/) est la méthode recommandée pour déployer OpenHEXA.

## Kubernetes

🚧 Pour le moment, les différents composants doivent être installés séparément. Nous travaillons actuellement sur un chart [Helm](https://helm.sh/) qui facilitera le déploiement d'OpenHEXA. En attendant, vous trouverez ci-dessous un aperçu de haut niveau de la façon dont OpenHEXA est déployé sur un cluster Kubernetes. N'hésitez pas à [nous contacter](https://github.com/BLSQ/openhexa/discussions) si vous avez besoin d'aide pour un déploiement OpenHEXA.

### Prérequis

Pour déployer OpenHEXA, vous aurez besoin de :

- Un cluster [Kubernetes](https://kubernetes.io/)
- Un serveur [PostgreSQL](https://www.postgresql.org/)
- Un moyen de provisionner du stockage objet, comme AWS S3, Google Cloud GCS ou un équivalent open source

### Déploiement de l'App

Le composant [openhexa-app](https://github.com/BLSQ/openhexa-app) est une application [Django](https://www.djangoproject.com/) plutôt standard. Le déploiement avec Kubernetes consiste à :

1. Créer un `Deployment` Kubernetes, un `Service` et l'exposer avec un `Ingress`
1. Créer une ressource `Deployment` pour la commande `datasources_worker`
1. Créer un `CronJob` dans Kubernetes pour les commandes `environment_sync` et `datasource_sync`
1. Créer un `Secret` et un `ConfigMap` pour les valeurs requises par le composant app (voir `settings.py` pour la référence des paramètres)

### Déploiement du Frontend

Le composant [openhexa-frontend](https://github.com/BLSQ/openhexa-frontend) est une application React [NextJS](https://nextjs.org/). Le déploiement avec Kubernetes consiste à :

1. Créer un `Deployment` Kubernetes, un `Service` et l'exposer avec un `Ingress`
1. Créer un `Secret` et un `ConfigMap` pour les valeurs requises par le composant app (voir `.env.local.dist` pour la référence des paramètres)

### Déploiement des Notebooks

La méthode recommandée pour déployer le composant notebooks d'OpenHEXA est d'utiliser le Helm Chart fourni par le projet [Zero To Kubernetes](https://zero-to-jupyterhub.readthedocs.io/en/latest/).

### Déploiement des Pipelines

La méthode recommandée pour déployer le composant pipeline d'OpenHEXA est d'utiliser le Helm Chart fourni par [Airflow](https://airflow.apache.org/docs/helm-chart/stable/index.html).

## Sur une machine unique

Il est possible d'installer OpenHexa sans Kubernetes sur une machine unique. Cela nécessite une distribution Linux récente basée sur Debian et Docker. Cette méthode est encore en cours de développement. Vous trouverez toutes les [instructions directement sur le projet principal OpenHexa](https://github.com/BLSQ/openhexa?tab=readme-ov-file#debian-package).
