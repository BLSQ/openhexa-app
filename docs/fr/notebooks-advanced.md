<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Utiliser les notebooks dans OpenHEXA</h1>
</div>
</div>

Le composant notebooks d'OpenHEXA est un déploiement [Jupyter](https://jupyter.org/) personnalisé.

Jupyter est un environnement de développement intégré flexible construit autour des notebooks – des documents qui combinent du code, de la documentation, des données et des visualisations enrichies. Il fournit un environnement interactif rapide pour le prototypage et l'explication du code, l'exploration et la visualisation des données et le partage d'idées avec d'autres. Pour plus d'informations sur la pile Jupyter, consultez la [documentation Jupyter officielle](https://docs.jupyter.org/en/latest/).

Vous pouvez utiliser des notebooks dans OpenHEXA pour diverses utilisations, telles que :

- Explorer et effectuer une analyse préliminaire d'un jeu de données
- Expliquer et illustrer un algorithme ou un modèle de données dans un style de [programmation littéraire](https://en.wikipedia.org/wiki/Literate_programming)
- Prototyper un tableau de bord de visualisation

Il existe quelques scénarios où vous pourriez envisager d'utiliser plutôt les [pipelines de données OpenHEXA](pipelines.md) :

- Si vous voulez permettre à des utilisateurs non techniques de lancer des workflows de traitement de données via une interface web
- Si vous voulez planifier l'exécution d'un workflow de données à des moments précis
- Lorsque vous avez besoin de pratiques standard de développement logiciel telles que le contrôle de version ou les tests unitaires

Le composant notebooks d'OpenHEXA fonctionne comme un environnement Jupyter standard, avec quelques ajouts intéressants, tels que :

- Il est livré avec de nombreuses bibliothèques préinstallées
- Le système de fichiers partagé de l'espace de travail est accessible dans le navigateur de fichiers Jupyter
- Les identifiants de la base de données de l'espace de travail sont automatiquement exposés sous forme de variables d'environnement

Le présent guide vous accompagnera à travers les spécificités de l'environnement notebooks d'OpenHEXA. Vous pouvez également trouver les deux guides suivants intéressants :

- [Utiliser le SDK OpenHEXA](sdk.md) : le SDK OpenHEXA est une bibliothèque Python qui fournit des blocs de construction et des méthodes utilitaires pour écrire du code sur OpenHEXA
- [Utiliser l'OpenHEXA Toolbox - DHIS2](toolbox-dhis2.md) : Acquérir et traiter des données depuis des instances DHIS2
- [Utiliser l'OpenHEXA Toolbox - IASO](toolbox-iaso.md) : Récupérer des données depuis IASO
- [Utiliser l'OpenHEXA Toolbox - Client OpenHEXA](toolbox-hexa.md) : Client GraphQL hérité (déprécié)

## Utiliser le système de fichiers de l'espace de travail

Lors du lancement de l'environnement notebooks, vous pouvez voir que le système de fichiers Jupyter affiche deux répertoires :

1. Le répertoire `tmp`
1. Le répertoire `workspace`

Vous ne pouvez écrire des données que dans ces deux répertoires : **il n'est pas possible de créer des fichiers ou des répertoires à la racine** du système de fichiers.

Veuillez consulter la [documentation SDK](sdk.md#reading-and-writing-files) pour plus d'informations sur les répertoires `workspace` et `tmp` et comment les utiliser avec Python (pour les utilisateurs R, consultez l'exemple de code ci-dessous, car nous n'avons pas encore de SDK pour R).

https://github.com/BLSQ/openhexa/assets/690667/8f279c1f-c371-490f-a04f-84a97b028859

Voici un exemple de base montrant comment lire / écrire des données vers le système de fichiers de l'espace de travail en Python :

```python
import pandas as pd
from openhexa.sdk import workspace

# Lire les données
df = pd.read_csv(f"{workspace.files_path}/covid_data.csv")

# Écrire les données
df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
df.to_csv(f"{workspace.files_path}/foobar.csv")
```

L'exemple R équivalent (jusqu'à ce que nous ayons un SDK pour R, vous devrez coder en dur le chemin du répertoire de l'espace de travail) :

```r
# Lire les données
df <- read.csv("/home/hexa/workspace/covid_data.csv")

# Écrire les données
x          <- 1:10
y          <- letters[1:10]
some_data <- tibble::tibble(x, y)
write.csv(some_data, "foobar.csv")
```

https://github.com/BLSQ/openhexa/assets/690667/49e53c15-c251-4283-9450-94ae9bdff9b6

## Utiliser la base de données de l'espace de travail

Comme la base de données de l'espace de travail est une base de données [PostgreSQL](https://www.postgresql.org/) standard, vous pouvez utiliser n'importe quelle bibliothèque
qui prend en charge PostgreSQL pour l'utiliser dans un notebook.

Si vous utilisez Python, la méthode recommandée pour récupérer les identifiants de la base de données est d'utiliser le [SDK OpenHEXA](sdk.md#using-the-workspace-database).

Voici un exemple Python minimal (avec [SQLAlchemy](https://www.sqlalchemy.org/)) pour vous lancer :

```python
import pandas as pd
from sqlalchemy import create_engine, Integer
from openhexa.sdk import workspace

# Créer un moteur SQLAlchemy
engine = create_engine(workspace.database_url)

# Lire les données
pd.read_sql("SELECT * FROM covid_data", con=engine)

# Écrire les données
df = pd.DataFrame({"foo": [1, 2, 3], "bar": [4, 5, 6]})
df.to_sql("a_new_table", con=engine, if_exists="replace", index_label="id",
          chunksize=100, dtype={"id": Integer(), "foo": Integer(), "bar": Integer()})
pd.read_sql("SELECT * FROM a_new_table", con=engine)
```

Notez que nous utilisons les arguments optionnels `chunksize` et `dtype` : `chunksize` pour contrôler le nombre de
lignes écrites dans chaque batch (pour optimiser l'utilisation de la mémoire), et `dtype` pour spécifier explicitement les types de colonnes PostgreSQL
et éviter les problèmes de conversion causés par le comportement de devinette de type par défaut.

Comme nous n'avons pas encore de SDK pour R, vous devrez utiliser des variables d'environnement pour obtenir les identifiants de la base de données avec R.

Voici comment vous pouvez le faire avec [DBI](https://dbi.r-dbi.org/) :

```r
# Connexion initiale
library(DBI)
con <- dbConnect(
    RPostgres::Postgres(),
    dbname = Sys.getenv("WORKSPACE_DATABASE_DB_NAME"),
    host = Sys.getenv("WORKSPACE_DATABASE_HOST"),
    port = Sys.getenv("WORKSPACE_DATABASE_PORT"),
    user = Sys.getenv("WORKSPACE_DATABASE_USERNAME"),
    password = Sys.getenv("WORKSPACE_DATABASE_PASSWORD")
)

# Écrire les données
x          <- 1:10
y          <- letters[1:10]
some_data <- tibble::tibble(x, y)
dbWriteTable(con, "another_table", some_data, overwrite=TRUE)
df <- dbReadTable(con, "another_table")
```

## Utiliser les connexions

Une fois que vous avez ajouté une nouvelle [connexion](connections.md), vous pourrez accéder à ses paramètres dans votre environnement Jupyter via le SDK.

Veuillez consulter la [documentation du SDK OpenHEXA](sdk.md#using-connections) pour plus d'informations sur l'utilisation des connexions en Python, et le [Manuel d'utilisation](connections.md) pour des informations générales sur l'utilisation des connexions.


Voici comment vous pouvez accéder aux paramètres de connexion en Python :

```python
import os
from openhexa.sdk import workspace

print(workspace.get_connection("connection-identifier"))
```

## Redémarrer votre serveur Jupyter

Il existe quelques situations où vous pourriez vouloir redémarrer votre serveur Jupyter, par exemple :

- Votre serveur est complètement bloqué et le redémarrer est votre dernière option

Malheureusement, redémarrer votre serveur Jupyter n'est pas vraiment simple pour le moment. Cela sera amélioré à l'avenir.

Pour l'instant, vous devrez :

1. Ouvrir le panneau de contrôle Jupyterhub (`File > Hub Control Panel`, s'ouvrira dans une nouvelle fenêtre ou un nouvel onglet)
1. Trouver votre serveur dans la liste des serveurs en cours d'exécution (chaque serveur de la liste correspond à un espace de travail ; le serveur que vous cherchez est dans l'état "running" et son nom doit correspondre à l'URL dans la barre d'adresse de votre navigateur)
1. Cliquer sur `stop`
1. Fermer l'onglet du Hub Control panel, retourner à l'écran des notebooks OpenHEXA et recharger la page

https://github.com/BLSQ/openhexa/assets/690667/18a6adfe-f44f-4bac-a71f-9127657a19d6

## Astuces et conseils

Cette section contient quelques recettes que vous pourriez trouver utiles.

## Utiliser s3fs pour interagir avec un bucket S3

Si vous avez besoin de parcourir, télécharger ou téléverser des données dans un bucket Amazon S3, la première étape est d'ajouter une [connexion](connections.md) AWS S3.

Une fois la connexion ajoutée, vous pourrez interagir avec le bucket dans un notebook Jupyter.

Bien que votre environnement Jupyter OpenHEXA soit livré avec [boto3](https://github.com/boto/boto3) préinstallé, pour la plupart des opérations, l'utilisation de [s3fs](https://github.com/fsspec/s3fs) sera plus simple (`s3fs` est également préinstallé dans votre environnement).

Voici un exemple de base montrant comment utiliser `s3fs` dans un notebook OpenHEXA :

```python
import os
import s3fs

# Les noms des variables d'environnement peuvent être copiés-collés depuis la page de détail de la connexion
fs = s3fs.S3FileSystem(key=os.environ["BUCKET_CONNECTION_ACCESS_KEY_ID"], secret=os.environ["BUCKET_CONNECTION_ACCESS_KEY_SECRET"])
bucket_name = os.environ["BUCKET_CONNECTION_BUCKET_NAME"]

# Lister les fichiers dans un répertoire du bucket
fs.ls(f"{bucket_name}/data/climate")

# Télécharger tous les fichiers du répertoire du bucket vers le système de fichiers de l'espace de travail
fs.get(f"{bucket_name}/data/climate", "/home/hexa/workspace/climate_data", recursive=True)
```

## Utiliser gcsfs pour interagir avec un bucket Google Cloud Storage

Si vous avez besoin de parcourir, télécharger ou téléverser des données dans un bucket Google Cloud Storage, la première étape est d'ajouter une [connexion](connections.md) GCS.

Une fois la connexion ajoutée, vous pourrez interagir avec le bucket dans un notebook Jupyter.

La méthode la plus simple pour interagir avec GCS est d'utiliser [gcsfs](https://github.com/fsspec/gcsfs) (`gcsfs` est préinstallé dans votre environnement).

Voici un exemple de base montrant comment utiliser `gcsfs` dans un notebook OpenHEXA :

```python
import gcsfs
import os
import json

# Les noms des variables d'environnement peuvent être copiés-collés depuis la page de détail de la connexion
gcsfs_service_account_key = json.loads(os.environ["BUCKET_CONNECTION_SERVICE_ACCOUNT_KEY"])
fs = gcsfs.GCSFileSystem(token=gcsfs_service_account_key)
bucket_name = os.environ["BUCKET_CONNECTION_BUCKET_NAME"]

# Lister les fichiers dans un répertoire du bucket
fs.ls(f"{bucket_name}/data/population")

# Télécharger tous les fichiers du répertoire du bucket vers le système de fichiers de l'espace de travail
fs.get(f"{bucket_name}/data/population", "/home/hexa/workspace/population_data", recursive=True)
```
