<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Utiliser le SDK OpenHEXA</h1>
</div>
</div>

Le SDK Python OpenHEXA est un outil qui vous aide à écrire du code pour la plateforme OpenHEXA.

Il est particulièrement utile pour écrire des pipelines de données OpenHEXA, mais peut également être utilisé dans l'environnement notebooks d'OpenHEXA.

## Démarrer

Le SDK OpenHEXA est installé par défaut dans votre environnement notebooks OpenHEXA (voir [Utiliser les notebooks dans OpenHEXA](notebooks-advanced.md) pour plus d'informations).

Si vous souhaitez l'utiliser uniquement dans les notebooks Jupyter, vous n'avez rien à installer vous-même.

Si vous souhaitez exécuter des pipelines OpenHEXA localement, veuillez consulter le guide [Écrire des pipelines OpenHEXA](writing-pipelines.md) pour les instructions d'installation.


## Lecture et écriture de fichiers {#reading-and-writing-files}

Dans votre environnement notebook et pipeline, deux répertoires sont exposés :

1. Le répertoire `workspace`
1. Le répertoire `tmp`

## Le répertoire workspace

Le répertoire `workspace` est le système de fichiers partagé de l'espace de travail, c'est là que la plupart de votre travail devrait avoir lieu. Le contenu de ce répertoire correspond à ce que vous pouvez voir dans l'onglet **Files** de l'interface OpenHEXA (voir la section [Gestion des fichiers dans les espaces de travail](files.md) du manuel d'utilisation pour plus d'informations).

Le système de fichiers de l'espace de travail est monté comme un système de fichiers ordinaire dans vos environnements notebook et pipeline — en d'autres termes, il n'y a rien de spécial à faire pour travailler avec les fichiers de l'espace de travail (bien qu'il y ait certaines considérations de performance à garder à l'esprit, voir ci-dessous).

Le SDK fournit une propriété simple sur l'objet global `workspace` pour obtenir le chemin du système de fichiers de l'espace de travail : `workspace.files_path`. Nous recommandons d'utiliser cette propriété lors de l'écriture ou de la lecture de fichiers, plutôt que de vous fier à des chemins codés en dur ou à des chemins relatifs.

Voici un exemple simple :

```python
from openhexa.sdk import workspace
import pandas as pd

# Lire les données
df = pd.read_csv(f"{workspace.files_path}/covid_data.csv")

# Écrire les données
df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
df.to_csv(f"{workspace.files_path}/foobar.csv")
```

## Le répertoire tmp

⚠️ Le répertoire `tmp` n'est pas persistant — tout son contenu sera supprimé lorsque votre serveur Jupyter s'arrêtera.

Le répertoire `tmp`, comme son nom l'indique, est destiné aux données temporaires. Vous pouvez l'utiliser comme système de fichiers éphémère pour la mise en cache ou le débogage, ou pour les téléchargements temporaires.

De plus, dans certains cas rares, le répertoire partagé de l'espace de travail ne peut pas être utilisé pour certaines opérations d'écriture. Cela peut arriver lors de l'utilisation de bibliothèques spécifiques. Dans ces situations, vous pouvez utiliser le dossier `tmp` pour l'écriture, puis copier les fichiers requis du répertoire `tmp` vers le répertoire `workspace`.

Vous pouvez obtenir le chemin absolu vers le répertoire `tmp` en utilisant la propriété `workspace.tmp_path`.

## Considérations d'implémentation et de performance

En coulisses, le système de fichiers de l'espace de travail utilise un système de stockage objet (généralement des buckets [Google Cloud Storage](https://cloud.google.com/storage)) monté avec une interface [FUSE](https://en.wikipedia.org/wiki/Filesystem_in_Userspace). Dans la plupart des cas, vous n'avez pas à vous soucier de ce détail d'implémentation. Cependant, bien que les performances de lecture et d'écriture d'une telle configuration soient généralement satisfaisantes, vous pourriez rencontrer des problèmes de performance lors de l'exécution d'un grand nombre de petites opérations d'écriture ou de lecture.

Un exemple d'un tel scénario est l'ouverture d'un fichier et l'exécution d'un grand nombre d'écritures en mode append. Si vous remarquez un ralentissement significatif de l'exécution en essayant de faire cela, vous pourriez envisager des alternatives :

- Construire le contenu du fichier en mémoire et l'écrire en une seule passe
- Utiliser le répertoire `tmp` pour les écritures append, et copier le fichier vers le répertoire `workspace` après

## Utiliser la base de données de l'espace de travail {#using-the-workspace-database}

Chaque espace de travail est livré avec une base de données [PostgreSQL](https://www.postgresql.org/) prête à l'emploi. Vous pouvez trouver des informations générales concernant cette base de données dans le [manuel d'utilisation](database.md).

L'extension géospatiale [PostGIS](https://postgis.net/) est installée sur chaque base de données d'espace de travail.

## Bases

Le SDK OpenHEXA ne fait pas grand-chose pour les opérations de base de données ; il vous permet simplement d'obtenir facilement les identifiants de la base de données,
que vous pouvez ensuite utiliser comme bon vous semble avec vos bibliothèques préférées.

La lecture ou l'écriture vers la base de données de l'espace de travail peut être effectuée avec l'utilitaire `workspace` :

```python
import pandas as pd
from sqlalchemy import create_engine, Integer, String
from openhexa.sdk import workspace

# Créer un moteur SQLAlchemy
engine = create_engine(workspace.database_url)

# Lire les données
pd.read_sql("SELECT * FROM covid_data", con=engine)

# Écrire les données
df = pd.DataFrame({"foo": [1, 2, 3], "bar": ["A", "B", "C"]})
df.to_sql("a_new_table", con=engine, if_exists="replace", index_label="id", chunksize=100,
          dtype={"foo": Integer(), "bar": String()})
pd.read_sql("SELECT * FROM a_new_table", con=engine)
```

Dans cet exemple, nous utilisons la méthode
[`pandas.Dataframe.to_sql`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html) pour écrire
des données vers la base de données de l'espace de travail. Vous êtes bien sûr libre d'utiliser toute autre bibliothèque qui peut se connecter à une base de données PostgreSQL.

Par défaut, toutes les lignes seront écrites en une fois lors de l'appel à `to_sql()`, ce qui peut entraîner une utilisation élevée de la mémoire.
Nous encourageons donc l'utilisation de l'argument `chunksize` comme dans l'exemple ci-dessus, qui vous permet de choisir le
nombre de lignes dans chaque batch à écrire à la fois.

Lorsque vous traitez un petit nombre de lignes, pour des cas d'usage simples et des expérimentations, nous vous encourageons également à utiliser l'argument `dtype` pour spécifier explicitement les types de colonnes PostgreSQL. Si vous ne le faites pas, pandas essaiera de deviner les types de colonnes Postgres à partir des types de colonnes du dataframe pandas, ce qui peut conduire à des conversions de type inattendues.

## Gérer votre modèle de données avec des colonnes et des index

Dès que vous traitez un nombre significatif de lignes, vous devriez envisager de définir explicitement votre modèle de données et d'utiliser des [index de base de données](https://www.postgresql.org/docs/current/indexes.html). Vous êtes libre de choisir comment gérer la création et la maintenance des index. Voici un exemple utilisant les [métadonnées SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/metadata.html) :

```python
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from openhexa.sdk import workspace
import pandas as pd

engine = create_engine(workspace.database_url)
metadata_obj = MetaData()

# Définir la table "letter frequency" et les index
letter_frequency = Table(
    "letter_frequency",
    metadata_obj,
    Column("letter", String(1), primary_key=True),
    Column("frequency", Integer(), nullable=False, index=True),
    Column("percentage", Float, nullable=False),
)
metadata_obj.create_all(engine)

# Préparer les données
df = pd.read_csv(f"{workspace.files_path}/letter_frequency.csv")
df["Letter"] = df["Letter"].str.replace('"', "")
df["Letter"] = df["Letter"].str.strip()
df = df.rename(columns={"Letter": "letter", ' "Frequency"': "frequency", ' "Percentage"': "percentage"})
df = df.set_index("letter")
df

# Sauvegarder dans la base de données
# con.execute("DELETE FROM...")
df.to_sql("letter_frequency", index_label="letter", con=engine, if_exists="append", dtype={"letter": String(1), "frequency": Integer(), "percentage": Float()})
```

## Utiliser les connexions {#using-connections}

L'utilitaire `workspace` offre plusieurs outils pour accéder aux différentes [connexions](connections.md) disponibles dans OpenHEXA.

Le tableau suivant montre, pour chaque type de connexion, le nom de la méthode associée sur l'utilitaire `workspace` et les champs disponibles :

|  Type               |  Nom de la méthode    |   Champ(s)                                                         |
| ------------------- | --------------------- | ------------------------------------------------------------------ |
| DHIS2               | dhis2_connection      |  `url` <br> `username` <br> `password`                             |
| PostgreSQL          | postgresql_connection |  `username` <br> `password` <br> `host` <br> `port` <br>`database_name`  |
| Bucket Amazon S3    | s3_connection         |  `bucket_name` <br> `access_key_id`  <br> `secret_access_key`      |
| Bucket Google Cloud | gcs_connection        |  `bucket_name` <br> `service_account_key`                          |
| Iaso                | iaso_connection       |  `url` <br> `username` <br> `password`                             |
| Personnalisée       | custom_connection     |  Voir ci-dessous                                                   |

Vous pouvez ensuite utiliser l'utilitaire `workspace` pour récupérer une connexion :

```python
from openhexa.sdk import workspace
import requests

dhis2_conn = workspace.dhis2_connection("conn-identifier")  # L'identifiant peut être trouvé dans l'écran de détail de la connexion
response = requests.get(f"{dhis2_conn.url}/api/...")

custom_conn = workspace.custom_connection("another-conn-identifier")

# ou vous pouvez utiliser l'API unifiée pour obtenir l'utilitaire de connexion
iaso_conn = workspace.get_connection("identifier")

# Les champs réels varieront en fonction des champs que vous avez définis sur votre connexion personnalisée
response = requests.get(f"{custom_conn.server_url}/{custom_conn.api_version}")
```

## Travailler avec les jeux de données {#working-with-datasets}

Voici un exemple d'utilisation du SDK OpenHEXA pour travailler avec un jeu de données :

```python
import pandas as pd
from openhexa.sdk.workspaces import workspace
from io import StringIO

# Créer un nouveau jeu de données
dataset = workspace.create_dataset("Test dataset", "Description")
print(dataset.slug)
# Si le jeu de données existe déjà
# dataset = workspace.get_dataset("test-dataset-42b690")

# Boucler sur les fichiers de la dernière version
for file in dataset.latest_version.files:
    print((file.filename, file.created_at))

# Obtenir un fichier unique
cities = dataset.latest_version.get_file("cities.csv")
cities_df = pd.read_csv(cities.download_url)

# Télécharger le fichier
with open(f"{workspace.files_path}/cities.csv", "wb") as cities_file:
    cities_file.write(cities.read())

# Boucler sur les versions existantes
for version in dataset.versions:
    print(version.name)

# Créer une nouvelle version
version = dataset.create_version("v1")

# Ajouter un fichier par chemin
version.add_file(f"{workspace.files_path}/cities.csv", filename = "cities.csv")

# Vérifier si un fichier existe
version.exists("cities.csv")

# Ajouter un fichier à la volée avec StringIO
df = pd.DataFrame({"name": ["Jane", "Jim", "Julia"], "age": [19,28,33]})
version.add_file(StringIO(df.to_csv(index=False)), filename="people.csv")
```

Les jeux de données peuvent également être fournis comme paramètres à un pipeline et peuvent être utilisés pour stocker la sortie d'un pipeline. Pour plus d'informations, voir le guide [Écrire des pipelines OpenHEXA](writing-pipelines.md).


## Travailler avec les webapps

Les webapps sont des applications web liées à votre espace de travail. Vous pouvez récupérer les informations d'une webapp de manière programmatique avec le SDK OpenHEXA.

L'utilitaire `workspace` fournit une méthode pour obtenir les informations d'une webapp par son identifiant slug :

```python
from openhexa.sdk import workspace

# Obtenir une webapp par son slug
webapp = workspace.get_webapp("my-dashboard")

# Accéder aux propriétés de la webapp
print(f"Name: {webapp.name}")
print(f"URL: {webapp.url}")
print(f"Description: {webapp.description}")
print(f"Icon: {webapp.icon}")
print(f"Is Favorite: {webapp.is_favorite}")

# Accéder aux informations du créateur
print(f"Created by: {webapp.created_by.display_name}")
print(f"Creator email: {webapp.created_by.email}")

# Accéder aux informations de l'espace de travail
print(f"Workspace: {webapp.workspace.name}")

# Vérifier les permissions
if webapp.permissions.update:
    print("You can update this webapp")
if webapp.permissions.delete:
    print("You can delete this webapp")
```

Si vous avez besoin de plus de contrôle ou si vous souhaitez utiliser le client GraphQL directement, vous pouvez également utiliser le `OpenHexaClient` :

```python
from openhexa.sdk import OpenHexaClient

client = OpenHexaClient()
webapp = client.get_webapp_by_slug(
    workspace_slug="my-workspace",
    webapp_slug="my-dashboard"
)

if webapp:
    print(f"Found webapp: {webapp.name}")
    print(f"URL: {webapp.url}")
else:
    print("Webapp not found")
```

Le slug de la webapp peut être trouvé dans la page de détail de la webapp dans l'interface OpenHEXA.


## Utiliser le client OpenHEXA {#using-the-openhexa-client}

Le SDK OpenHEXA fournit une interface client qui vous permet d'interagir programmatiquement avec la plateforme OpenHEXA pour gérer des espaces de travail, des pipelines, des jeux de données et d'autres ressources.

Vous bénéficiez d'un grand nombre de méthodes typées, facilitant la découverte et les intégrations :

![Screenshot 2025-06-27 at 17 00 07](https://github.com/user-attachments/assets/cd2e530e-ba4f-46d5-aa4f-695ae52eb92c)


## Utilisation de base

```python
  from openhexa.sdk.client import openhexa

  # Le client est automatiquement configuré à l'aide des variables d'environnement
  # HEXA_SERVER_URL et HEXA_TOKEN (définies dans les notebooks/pipelines)

  workspaces_response = openhexa.workspaces()

  for workspace in workspaces_response.items:
      print(f"Workspace: {workspace.name} ({workspace.slug})")
      print(f"  Description: {workspace.description}")
      print(f"  Countries: {workspace.countries}")
```

## Exemple de cas d'usage : un pipeline qui attend la fin des dernières exécutions

```python
from time import sleep

from openhexa.graphql import PipelineRunStatus
from openhexa.sdk import pipeline, workspace as current_workspace, current_run
from openhexa.sdk.client import openhexa

POLL_INTERVAL = 10


@pipeline(name="patient_pipeline")
def patient_pipeline():
    """Un pipeline patient simple qui attend la fin des autres exécutions."""
    current_run.log_info("Started waiting for my turn")
    while len([run for run in openhexa.pipeline(workspace_slug=current_workspace.slug, pipeline_code="patient-pipeline").runs.items if run.status == PipelineRunStatus.running]) > 1:
        current_run.log_info(f"Still waiting... checking again in {POLL_INTERVAL}s")
        sleep(POLL_INTERVAL)
    current_run.log_info("No running pipeline, proceeding...")

if __name__ == "__main__":
    patient_pipeline()
```

## Gérer les pipelines

```python
  from openhexa.sdk.client import openhexa

  pipelines_response = openhexa.pipelines(workspace_slug="testabcd", page=1, per_page=10)
  print(f"Pages: {pipelines_response.total_pages}")

  for pipeline in pipelines_response.items:
      print(f"Pipeline: {pipeline.name} ({pipeline.code})")
      print(f"  Type: {pipeline.type}")

      if pipeline.current_version:
          print(f"  Current version: {pipeline.current_version.name}")
          print(f"  Version number: {pipeline.current_version.version_number}")

  pipeline_details = openhexa.pipeline(workspace_slug="testabcd", pipeline_code="bikes-in-brussels")
  if pipeline_details:
      print(f"Pipeline: {pipeline_details.name}")
      print(f"Schedule : {pipeline_details.schedule}")

  create_response = openhexa.create_pipeline({
      "workspaceSlug": "testabcd",
      "name": "My New Pipeline",
      "code": "my-new-pipeline"
  })

  if create_response.success:
      new_pipeline = create_response.pipeline
      print(f"Created pipeline: {new_pipeline.code}")

      pipeline_details = openhexa.pipeline(workspace_slug="testabcd", pipeline_code=new_pipeline.code)
  else:
      print(f"Failed to create pipeline: {create_response.errors}")

  if pipeline_details:
      delete_response = openhexa.delete_pipeline({"id": pipeline_details.id})
      if delete_response.success:
          print("Pipeline deleted successfully")
      else:
          print(f"Failed to delete pipeline: {delete_response.errors}")
```

## Gérer les jeux de données avec des réponses typées

```python
  from openhexa.sdk.client import openhexa

  datasets_response = openhexa.datasets(page=1)

  for dataset in datasets_response.items:
      print(f"Dataset: {dataset.name} ({dataset.slug})")
      print(f"  Created: {dataset.created_at}")
      print(f"  Updated: {dataset.updated_at}")
      print(f"  Created by : {dataset.created_by.display_name}")

  dataset = openhexa.dataset(id=datasets_response.items[0].id)
  if dataset:
      print(f"Dataset: {dataset.name}")

      if dataset.versions:
          print(f"Total versions: {len(dataset.versions.items)}")
          for version in dataset.versions.items:
              print(f"  Version: {version.name} - Created: {version.created_at}")


  create_response = openhexa.create_dataset({
      "workspaceSlug": "testabcd",
      "name": "My Dataset",
      "description": "Dataset description"
  })

  if create_response.success:
      new_dataset = create_response.dataset
      print(f"Created dataset: {new_dataset.name} (slug: {new_dataset.slug})")
```

## Gérer la configuration de l'espace de travail

Vous pouvez obtenir et gérer le dictionnaire de configuration de l'espace de travail pour définir et utiliser des propriétés à l'échelle de l'espace de travail.
Voici un exemple d'une propriété `SNT_PIPELINE_COUNT` qui a été configurée pour l'espace de travail.

```python
from openhexa.sdk import workspace

# configuration est un dictionnaire JSON qui peut être manipulé comme tel
config = workspace.configuration
if "SNT_PIPELINE_COUNT" in config:
    print(config.get("SNT_PIPELINE_COUNT"))
    # Pour mettre à jour la propriété
    config["SNT_PIPELINE_COUNT"] = 10
    workspace.configuration = config
```

## Gérer les espaces de travail et les membres

```python
from openhexa.sdk.client import openhexa

workspaces_response = openhexa.workspaces()
for workspace in workspaces_response.items:
    print(f"Workspace: {workspace.name}")

    detailed_workspace = openhexa.workspace(slug=workspace.slug)
    print(f"  Countries: {detailed_workspace.countries}")

create_response = openhexa.create_workspace({
      "name": "My New Workspace",
      "description": "Workspace for data analysis"
  })

if create_response.success:
    new_workspace = create_response.workspace
    print(f"Created workspace: {new_workspace.name}")

    invite_response = openhexa.invite_workspace_member({
        "workspaceSlug": new_workspace.slug,
        "userEmail": "newuser@bluesuqare.org",
        "role": "EDITOR"
    })
```

## Utilisation avancée

Si vous souhaitez obtenir d'autres actions/attributs de cette bibliothèque, n'hésitez pas à demander à l'équipe OpenHexa de les inclure. Ils ont des moyens simples et automatisés pour étendre cette bibliothèque efficacement.
En attendant, vous pouvez exécuter des requêtes GraphQL personnalisées pour des cas d'usage avancés non couverts par les méthodes du client prédéfinies :

```python
  from openhexa.sdk.client import openhexa

  custom_query = """
  query getWorkspaceStats($workspaceSlug: String!) {
      workspace(slug: $workspaceSlug) {
          name
          slug
          datasets {
              items {
               dataset {
                name
               }
              }
          }
      }
  }
  """

  result = openhexa.execute(
      query=custom_query,
      variables={"workspaceSlug": "testabcd"}
  )
  for dataset in result.json()["data"]["workspace"]["datasets"]["items"]:
      print(f"Dataset name {dataset["dataset"]["name"]}")
```
