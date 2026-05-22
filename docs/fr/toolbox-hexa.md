<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>OpenHEXA Toolbox - Client OpenHEXA (n'est plus maintenu)</h1>
</div>

_⚠️ Nous recommandons désormais d'utiliser le [Client OpenHexa du SDK](sdk.md#using-the-openhexa-client) à la place. Il contient de nombreuses méthodes (typées) et peut être étendu de manière semi-automatique par l'équipe OpenHexa. Le client toolbox ne sera pas maintenu/étendu à l'avenir._

La classe OpenHEXA fait partie du toolbox OpenHexa, conçue pour interagir avec l'API de la plateforme OpenHexa.
Le module OpenHEXAClient permet aux utilisateurs d'interagir avec le backend OpenHEXA en utilisant la syntaxe GraphQL.

## Installation

``` sh
pip install openhexa.toolbox
```

## Usage

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
