<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Client IASO</h1>
</div>

[`iaso-client`](https://github.com/BLSQ/iaso-client) est la bibliothèque Python recommandée pour récupérer des données depuis IASO. Elle s'authentifie auprès d'une instance IASO et donne un accès typé aux unités d'organisation, types d'unités d'organisation, formulaires, versions de formulaires et soumissions de formulaires (instances), avec pagination automatique, sortie en DataFrame pandas et exports CSV/XLSX.

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

Chaque ressource expose des méthodes `*_list()` et `*_retrieve()`. Les filtres sont passés en arguments nommés.

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

### Pagination

- `*_list()` récupère et agrège les résultats de toutes les pages.
- `*_list(page=...)` renvoie une seule page de résultats (JSON uniquement).
- `max_page_size` contrôle la taille des pages et doit être compris entre `50` et `2000`.

``` python
first_page = client.org_units_list(page=1, max_page_size=500)
```

### Obtenir un DataFrame pandas

``` python
df = client.instances_list(form_id=276, format="dataframe")
```

### Exporter en CSV ou XLSX

Les unités d'organisation, formulaires et instances peuvent être exportés directement dans un fichier via les endpoints d'export d'IASO :

``` python
client.org_units_list(format="csv", output_path=f"{workspace.files_path}/org_units.csv")
client.instances_list(format="xlsx", form_id=276, output_path=f"{workspace.files_path}/submissions")
```

`output_path` doit être un chemin de fichier : son répertoire parent doit exister et le fichier ne doit pas déjà exister. L'extension `.csv` ou `.xlsx` est ajoutée si elle est omise.

### Endpoints sans méthode typée

Utilisez `raw()` pour appeler n'importe quel endpoint `GET` d'IASO, relatif à `/api/` :

``` python
entities = client.raw("entities/", params={"entity_type_ids": 12}, page=1, max_page_size=100)
```

Consultez le [dépôt iaso-client](https://github.com/BLSQ/iaso-client) pour la liste complète des méthodes et des filtres.

## Migrer depuis `openhexa.toolbox.iaso`

| `openhexa.toolbox.iaso`                                   | `iaso-client`                                                        |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| `IASO(url, username, password)`                           | `client = IasoClient(base_url=url)` <br> `client.login(username, password)` |
| `iaso.get_org_units(...)`                                 | `client.org_units_list(...)`                                         |
| `iaso.get_forms(org_units=[...], projects=[...])`         | `client.forms_list(org_unit_id=..., projects_ids=[...])`             |
| `iaso.get_form_instances(..., as_dataframe=True)`         | `client.instances_list(..., format="dataframe")`                     |
| `iaso.get_projects()`                                     | `client.raw("projects/")`                                            |
