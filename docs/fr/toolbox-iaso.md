<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Client IASO</h1>
</div>

[`iaso-client`](https://github.com/BLSQ/iaso-client) est la bibliothèque Python recommandée pour récupérer des données depuis IASO. Elle s'authentifie auprès d'une instance IASO et donne un accès typé aux unités d'organisation, types d'unités d'organisation, formulaires, versions de formulaires et soumissions de formulaires (instances), avec pagination automatique.

!!! warning "`openhexa.toolbox.iaso` est déprécié"
    La classe `IASO` de `openhexa.toolbox.iaso` n'est plus maintenue. Utilisez `iaso-client` pour les nouveaux pipelines et notebooks, et migrez le code existant lorsque c'est possible (voir [Migrer depuis `openhexa.toolbox.iaso`](#migrer-depuis-openhexatoolboxiaso)).

## Installation

`iaso-client` est préinstallé dans les images de notebooks et de pipelines OpenHEXA. Pour l'utiliser ailleurs (ou pour fixer une version spécifique dans le `requirements.txt` d'un pipeline) :

``` sh
pip install iaso-client
```

## Usage

### Connexion à une instance

Créez un `IasoClient` avec l'URL de base de l'instance IASO (sans slash final), puis appelez `login()`. Le jeton est conservé et réutilisé pour toutes les requêtes suivantes.

Dans un workspace OpenHEXA, stockez les identifiants dans une [connexion IASO](connections.md) et lisez-les avec le SDK :

``` python
from openhexa.sdk import workspace
from iaso_client import IasoClient

con = workspace.iaso_connection("identifiant-connexion-iaso")

client = IasoClient(base_url=con.url.rstrip("/"))
client.login(con.username, con.password)
```

### Lire des données

Chaque ressource expose des méthodes `*_list()` et `*_retrieve()`. `*_list()` récupère toutes les pages et renvoie tous les éléments correspondants sous forme de liste. Les filtres sont passés en arguments nommés.

``` python
# Unités d'organisation
org_units = client.org_units_list(org_unit_type_id=5, project=149)
org_unit = client.org_units_retrieve(org_unit_id=781)

# Types d'unités d'organisation
org_unit_types = client.org_unit_types_list(project=149)

# Formulaires et versions de formulaires
forms = client.forms_list(projects_ids=[149])
form = client.forms_retrieve(form_id=276)
form_versions = client.form_versions_list(form_id=276)

# Soumissions de formulaires (instances)
instances = client.instances_list(form_id=276, date_from="2025-01-01")
instance = client.instances_retrieve(instance_id=12345)
```

### Obtenir un DataFrame pandas

`*_list()` renvoie une liste de dictionnaires, qui peut être chargée dans un DataFrame :

``` python
import pandas as pd

df = pd.json_normalize(client.instances_list(form_id=276))
```

Consultez le [dépôt iaso-client](https://github.com/BLSQ/iaso-client) pour la liste complète des filtres.

## Migrer depuis `openhexa.toolbox.iaso`

| `openhexa.toolbox.iaso`                                   | `iaso-client`                                                        |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| `IASO(url, username, password)`                           | `client = IasoClient(base_url=url)` <br> `client.login(username, password)` |
| `iaso.get_org_units(...)`                                 | `client.org_units_list(...)`                                         |
| `iaso.get_forms(org_units=[...], projects=[...])`         | `client.forms_list(org_unit_id=..., projects_ids=[...])`             |
| `iaso.get_form_instances(..., as_dataframe=True)`         | `pd.json_normalize(client.instances_list(...))`                      |
