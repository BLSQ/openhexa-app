<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Client OpenHEXA</h1>
</div>

Le SDK OpenHEXA fournit un `OpenHexaClient` typé pour interagir programmatiquement avec la plateforme OpenHEXA — workspaces, pipelines, exécutions, datasets et webapps — avec un typage complet. Il remplace l'ancien client `openhexa.toolbox.hexa`.

L'ensemble des méthodes typées est documenté dans le [guide SDK](sdk.md#using-the-openhexa-client) ; cette page couvre l'installation, l'authentification et un tour rapide. L'ancien client `openhexa.toolbox.hexa` est conservé en bas de page pour référence.

## Installation

Le client fait partie du package `openhexa.sdk` :

```sh
pip install openhexa.sdk
```

## Authentification

Dans les notebooks et pipelines OpenHEXA, le client est configuré automatiquement à partir des variables d'environnement `HEXA_SERVER_URL` et `HEXA_TOKEN`. En exécution locale, définissez ces variables vous-même (par exemple via `openhexa config set_url` et `openhexa config set_token`) ou instanciez le client explicitement :

```python
from openhexa.sdk import OpenHexaClient

client = OpenHexaClient(server_url="https://app.demo.openhexa.org", token="votre-token")
```

## Utilisation

Le point d'entrée recommandé est l'instance `openhexa` prête à l'emploi, qui récupère la configuration depuis l'environnement :

```python
from openhexa.sdk.client import openhexa

workspaces_response = openhexa.workspaces()
for workspace in workspaces_response.items:
    print(f"{workspace.slug} — {workspace.name}")

pipelines_response = openhexa.pipelines(workspace_slug="mon-workspace", page=1, per_page=10)
for pipeline in pipelines_response.items:
    print(f"{pipeline.code} : {pipeline.name}")

pipeline_details = openhexa.pipeline(workspace_slug="mon-workspace", pipeline_code="bikes-in-brussels")
if pipeline_details:
    print(f"Planification : {pipeline_details.schedule}")

datasets_response = openhexa.datasets(page=1)
for dataset in datasets_response.items:
    print(f"{dataset.slug} — {dataset.name}")
```

Le client expose un grand nombre de méthodes typées, facilitant la découverte et l'intégration :

![Screenshot 2025-06-27 at 17 00 07](https://github.com/user-attachments/assets/cd2e530e-ba4f-46d5-aa4f-695ae52eb92c)

Consultez le [guide SDK](sdk.md#using-the-openhexa-client) pour des exemples complets (gestion des pipelines, datasets, exécutions et webapps).

---

## Déprécié : `openhexa.toolbox.hexa`

> ⚠️ **Déprécié** — le client GraphQL `openhexa.toolbox.hexa.OpenHEXA` n'est plus maintenu. Utilisez l'`OpenHexaClient` ci-dessus pour tout nouveau code et migrez l'existant lorsque c'est possible. Le contenu ci-dessous est conservé uniquement à titre de référence pour les projets qui en dépendent encore.

### Installation

```sh
pip install openhexa.toolbox
```

### Connexion à l'API

Pour initialiser la classe OpenHEXA, vous devez fournir le server_url de l'instance OpenHexa et soit une combinaison nom d'utilisateur/mot de passe, soit un jeton API pour l'authentification.
L'authentification à deux facteurs doit être désactivée pour cette méthode.

```python
from openhexa.toolbox.hexa import OpenHEXA
# Nous pouvons nous authentifier avec nom d'utilisateur / mot de passe
hexa = OpenHEXA("https://app.demo.openhexa.org", username="username",  password="password")

# Vous pouvez également utiliser le jeton fourni par OpenHEXA sur la page des pipelines.
hexa = OpenHEXA("https://app.demo.openhexa.org", token="token")
```

### Jouer avec l'API

Après avoir importé le module Hexa, vous pouvez utiliser la méthode fournie pour récupérer les Projects, Organisation Units et Forms pour lesquels vous avez
des permissions.

```python
from openhexa.toolbox.hexa import OpenHEXA
# Obtenir les espaces de travail
workspaces = hexa.get_workspaces()

# Obtenir les pipelines dans un espace de travail spécifique
workspace_slug = workspaces['workspaces']['items'][0]['slug']
pipelines = hexa.get_pipelines(workspace_slug)

# Exécuter un pipeline
pipeline_id = pipelines['pipelines']['items'][0]['id']
run_response = hexa.run_pipeline(id=pipeline_id,config={}, send_notification=True)

print(run_response)
```