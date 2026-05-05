<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Utiliser le Toolbox OpenHEXA</h1>
</div>
</div>

# OpenHEXA Toolbox DHIS2

Une bibliothèque utilitaire pour acquérir et traiter des données depuis une instance DHIS2.

## Installation

``` sh
pip install openhexa.toolbox
```

## Usage

### Connexion à une instance

Des identifiants sont requis pour initialiser une connexion à une instance DHIS2, et doivent être fournis via un objet `Connection`.

Dans un espace de travail OpenHEXA (par exemple dans un pipeline OpenHEXA ou un notebook OpenHEXA), un objet `Connection` peut être créé via le SDK OpenHEXA en fournissant l'identifiant de la connexion d'espace de travail.

![OpenHEXA workspace connection](https://github.com/BLSQ/openhexa/blob/main/visuals/connection_id.png?raw=true)

``` python
>>> from openhexa.sdk import workspace
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion dans un espace de travail OpenHEXA
>>> con = workspace.dhis2_connection("DHIS2_PLAY")
>>> dhis = DHIS2(con)
```

En dehors d'un espace de travail OpenHEXA, une connexion peut être créée manuellement via le SDK en fournissant l'URL de l'instance, un nom d'utilisateur et un mot de passe.


``` python
>>> from openhexa.sdk.workspaces.connections import DHIS2Connection
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion en dehors d'un espace de travail OpenHEXA
>>> con = DHIS2Connection(url="https://play.dhis2.org/40.0.1", username="admin", password="district")
>>> dhis = DHIS2(con)
```

Si nécessaire, la dépendance au SDK OpenHEXA peut être contournée en fournissant un `namedtuple` au lieu d'un objet `Connection`.

``` python
>>> from collections import namedtuple
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion en dehors d'un espace de travail OpenHEXA
>>> Connection = namedtuple("Connection", ["url", "username", "password"])
>>> con = Connection(url="https://play.dhis2.org/40.0.1", username="admin", password="district")
>>> dhis = DHIS2(con)
```

### Mise en cache

La mise en cache peut être activée en fournissant un répertoire de cache lors de l'initialisation d'une nouvelle connexion.

``` python
>>> from openhexa.sdk import workspace
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion dans un espace de travail OpenHEXA
>>> con = workspace.dhis2_connection("DHIS2_PLAY")
>>> dhis = DHIS2(con, cache_dir=".cache")
```

À ce jour, la bibliothèque ne met en cache que les métadonnées de l'instance et ne gère pas les requêtes de données.

### Lire les métadonnées

Les métadonnées de l'instance peuvent être accédées via un ensemble de méthodes sous le namespace `DHIS2.meta`. Les métadonnées sont toujours retournées sous forme d'objets de type JSON qui peuvent facilement être convertis en dataframes Pandas ou Polars.

``` python
>>> import polars as pl
>>> from openhexa.sdk import workspace
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion dans un espace de travail OpenHEXA
>>> con = workspace.dhis2_connection("DHIS2_PLAY")
>>> dhis = DHIS2(con, cache_dir=".cache")

>>> # lire les métadonnées des unités d'organisation
>>> org_units = dhis.meta.organisation_units()
>>> df = pl.DataFrame(org_units)

>>> print(df)

shape: (1_332, 5)
┌─────────────┬──────────────────────┬───────┬─────────────────────────────────┬───────────────────┐
│ id          ┆ name                 ┆ level ┆ path                            ┆ geometry          │
│ ---         ┆ ---                  ┆ ---   ┆ ---                             ┆ ---               │
│ str         ┆ str                  ┆ i64   ┆ str                             ┆ str               │
╞═════════════╪══════════════════════╪═══════╪═════════════════════════════════╪═══════════════════╡
│ Rp268JB6Ne4 ┆ Adonkia CHP          ┆ 4     ┆ /ImspTQPwCqd/at6UHUQatSo/qtr8GG ┆ null              │
│             ┆                      ┆       ┆ l…                              ┆                   │
│ cDw53Ej8rju ┆ Afro Arab Clinic     ┆ 4     ┆ /ImspTQPwCqd/at6UHUQatSo/qtr8GG ┆ null              │
│             ┆                      ┆       ┆ l…                              ┆                   │
│ GvFqTavdpGE ┆ Agape CHP            ┆ 4     ┆ /ImspTQPwCqd/O6uvpzGd5pu/U6Kr7G ┆ null              │
│             ┆                      ┆       ┆ t…                              ┆                   │
│ plnHVbJR6p4 ┆ Ahamadyya Mission Cl ┆ 4     ┆ /ImspTQPwCqd/PMa2VCrupOd/QywkxF ┆ {"type": "Point", │
│             ┆                      ┆       ┆ u…                              ┆ "coordinates":…   │
│ …           ┆ …                    ┆ …     ┆ …                               ┆ …                 │
│ hDW65lFySeF ┆ Youndu CHP           ┆ 4     ┆ /ImspTQPwCqd/jmIPBj66vD6/Z9QaI6 ┆ null              │
│             ┆                      ┆       ┆ s…                              ┆                   │
│ Urk55T8KgpT ┆ Yoyah CHP            ┆ 4     ┆ /ImspTQPwCqd/jUb8gELQApl/yu4N82 ┆ null              │
│             ┆                      ┆       ┆ F…                              ┆                   │
│ VdXuxcNkiad ┆ Yoyema MCHP          ┆ 4     ┆ /ImspTQPwCqd/jmIPBj66vD6/USQdmv ┆ {"type": "Point", │
│             ┆                      ┆       ┆ r…                              ┆ "coordinates":…   │
│ BNFrspDBKel ┆ Zimmi CHC            ┆ 4     ┆ /ImspTQPwCqd/bL4ooGhyHRQ/BD9gU0 ┆ {"type": "Point", │
│             ┆                      ┆       ┆ G…                              ┆ "coordinates":…   │
└─────────────┴──────────────────────┴───────┴─────────────────────────────────┴───────────────────┘
```

Les types de métadonnées suivants sont pris en charge :
* `DHIS2.meta.system_info()`
* `DHIS2.meta.organisation_units()`
* `DHIS2.meta.organisation_unit_groups()`
* `DHIS2.meta.organisation_unit_levels()`
* `DHIS2.meta.datasets()`
* `DHIS2.meta.data_elements()`
* `DHIS2.meta.data_element_groups()`
* `DHIS2.meta.indicators()`
* `DHIS2.meta.indicator_groups()`
* `DHIS2.meta.category_option_combos()`

### Lire les données

Les données peuvent être accédées via deux endpoints distincts : [`dataValueSets`](https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-240/data.html#webapi_reading_data_values) et [`analytics`](https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-240/analytics.html). L'endpoint `dataValueSets` permet d'interroger les valeurs de données brutes stockées dans la base de données DHIS2, tandis qu'`analytics` peut accéder aux données agrégées stockées dans les tables analytiques DHIS2.

#### Data value sets

Les valeurs de données brutes peuvent être lues à l'aide de la méthode `DHIS2.data_value_sets.get()`. La méthode accepte les arguments suivants :

* **`data_elements`** : *list of str, optional*<br>
    Identifiants des data elements (nécessite DHIS2 >= 2.39)


* **`datasets`** : *list of str, optional*<br>
    Identifiants des datasets

* **`data_element_groups`** : *str, optional*<br>
    Identifiants des groupes de data elements

* **`periods`** : *list of str, optional*<br>
    Identifiants de période au format ISO

* **`start_date`** : *str, optional*<br>
    Date de début pour la plage temporelle des valeurs à exporter

* **`end_date`** : *str, optional*<br>
    Date de fin pour la plage temporelle des valeurs à exporter

* **`org_units`** : *list of str, optional*<br>
    Identifiants des unités d'organisation

* **`org_unit_groups`** : *list of str, optional*<br>
    Identifiants des groupes d'unités d'organisation

* **`children`** : *bool, optional (default=False)*<br>
    Inclure ou non les enfants dans la hiérarchie des unités d'organisation

* **`attribute_option_combos`** : *list of str, optional*<br>
    Identifiants des attribute option combos

* **`last_updated`** : *str, optional*<br>
    Inclure uniquement les valeurs de données mises à jour depuis l'horodatage donné

* **`last_updated_duration`** : *str, optional*<br>
    Inclure uniquement les valeurs de données mises à jour dans la durée donnée. Le
    format est <value><time-unit>, où les unités de temps prises en charge sont "d" (jours),
    "h" (heures), "m" (minutes) et "s" (secondes).

Au moins 3 arguments doivent être fournis :
* Un dans la dimension data (`data_elements`, `data_element_groups` ou `datasets`)
* Un dans la dimension spatiale (`org_units` ou `org_unit_groups`)
* Un dans la dimension temporelle (`periods` ou `start_date` et `end_date`)

Les valeurs de données sont retournées sous forme de liste de dictionnaires JSON-like qui peuvent être convertis en dataframe Pandas ou Polars.

```python
>>> import polars as pl
>>> from openhexa.sdk import workspace
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion dans un espace de travail OpenHEXA
>>> con = workspace.dhis2_connection("DHIS2_PLAY")
>>> dhis = DHIS2(con, cache_dir=".cache")

>>> data_values = dhis.data_value_sets.get(
...     datasets=["QX4ZTUbOt3a"],
...     org_units=["JQr6TJx5KE3", "KbO0JnhiMwl", "f90eISKFm7P"],
...     start_date="2022-01-01",
...     end_date="2022-04-01"
... )

>>> print(len(data_values))
301

>>> print(data_values[0])
{
    'dataElement': 'zzHwXqxKYy1', 'period': '202201', 'orgUnit': 'JQr6TJx5KE3', 'categoryOptionCombo': 'r8xySVHExGT', 'attributeOptionCombo': 'HllvX50cXC0', 'value': '2', 'storedBy': 'kailahun1', 'created': '2010-03-07T00:00:00.000+0000', 'lastUpdated': '2010-03-07T00:00:00.000+0000', 'comment': '', 'followup': False
}

>>> df = pl.DataFrame(data_values)
>>> print(df)

shape: (301, 11)
┌────────────┬────────┬────────────┬────────────┬───┬────────────┬────────────┬─────────┬──────────┐
│ dataElemen ┆ period ┆ orgUnit    ┆ categoryOp ┆ … ┆ created    ┆ lastUpdate ┆ comment ┆ followup │
│ t          ┆ ---    ┆ ---        ┆ tionCombo  ┆   ┆ ---        ┆ d          ┆ ---     ┆ ---      │
│ ---        ┆ str    ┆ str        ┆ ---        ┆   ┆ str        ┆ ---        ┆ str     ┆ bool     │
│ str        ┆        ┆            ┆ str        ┆   ┆            ┆ str        ┆         ┆          │
╞════════════╪════════╪════════════╪════════════╪═══╪════════════╪════════════╪═════════╪══════════╡
│ zzHwXqxKYy ┆ 202201 ┆ JQr6TJx5KE ┆ r8xySVHExG ┆ … ┆ 2010-03-07 ┆ 2010-03-07 ┆         ┆ false    │
│ 1          ┆        ┆ 3          ┆ T          ┆   ┆ T00:00:00. ┆ T00:00:00. ┆         ┆          │
│            ┆        ┆            ┆            ┆   ┆ 000+0000   ┆ 000+0000   ┆         ┆          │
│ …          ┆ …      ┆ …          ┆ …          ┆ … ┆ …          ┆ …          ┆ …       ┆ …        │
└────────────┴────────┴────────────┴────────────┴───┴────────────┴────────────┴─────────┴──────────┘
```

#### Analytics

Les données agrégées des tables Analytics peuvent être lues à l'aide de la méthode `DHIS2.analytics.get()`. La méthode accepte les arguments suivants :

* **`data_elements`** : *list of str, optional*<br>
    Identifiants des data elements

* **`data_element_groups`** : *list of str, optional*<br>
    Identifiants des groupes de data elements

* **`indicators`**: *list of str, optional*<br>
    Identifiants des indicateurs

* **`indicator_groups`**: *list of str, optional*<br>
    Identifiants des groupes d'indicateurs

* **`periods`** : *list of str, optional*<br>
    Identifiants de période au format ISO

* **`org_units`** : *list of str, optional*<br>
    Identifiants des unités d'organisation

* **`org_unit_groups`** : *list of str, optional*<br>
    Identifiants des groupes d'unités d'organisation

* **`org_unit_levels`** : *list of int, optional*<br>
    Niveaux des unités d'organisation

* **`include_cocs`** : *bool, optional (default=True)*<br>
    Inclure les category option combos dans la réponse

Au moins 3 arguments doivent être fournis :
* Un dans la dimension data (`data_elements`, `data_element_groups`, `indicators` ou `indicator_groups`)
* Un dans la dimension spatiale (`org_units`, `org_unit_groups` ou `org_unit_levels`)
* Un dans la dimension temporelle (`periods`)

Les valeurs de données sont retournées sous forme de liste de dictionnaires JSON-like qui peuvent être convertis en dataframe Pandas ou Polars.

```python
>>> import polars as pl
>>> from openhexa.sdk import workspace
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion dans un espace de travail OpenHEXA
>>> con = workspace.dhis2_connection("DHIS2_PLAY")
>>> dhis = DHIS2(con, cache_dir=".cache")

>>> data_values = play.analytics.get(
...     data_elements=["V37YqbqpEhV", "tn3p7vIxoKY", "HZSdnO5fCUc"],
...     org_units=["JQr6TJx5KE3", "KbO0JnhiMwl", "f90eISKFm7P"],
...     periods=["202201", "202202", "202203"]
... )

>>> df = pl.DataFrame(data_values)
>>> print(df)

shape: (14, 5)
┌─────────────┬─────────────┬─────────────┬────────┬───────┐
│ dx          ┆ co          ┆ ou          ┆ pe     ┆ value │
│ ---         ┆ ---         ┆ ---         ┆ ---    ┆ ---   │
│ str         ┆ str         ┆ str         ┆ str    ┆ str   │
╞═════════════╪═════════════╪═════════════╪════════╪═══════╡
│ V37YqbqpEhV ┆ PT59n8BQbqM ┆ JQr6TJx5KE3 ┆ 202201 ┆ 5     │
│ V37YqbqpEhV ┆ pq2XI5kz2BY ┆ f90eISKFm7P ┆ 202201 ┆ 4     │
│ V37YqbqpEhV ┆ PT59n8BQbqM ┆ f90eISKFm7P ┆ 202201 ┆ 11    │
│ V37YqbqpEhV ┆ pq2XI5kz2BY ┆ JQr6TJx5KE3 ┆ 202201 ┆ 2     │
│ …           ┆ …           ┆ …           ┆ …      ┆ …     │
└─────────────┴─────────────┴─────────────┴────────┴───────┘
```

### Joindre des champs de métadonnées

#### Noms

Des méthodes utilitaires pour ajouter des colonnes de noms en plus des identifiants sont disponibles sous le namespace `DHIS.meta` :

* `DHIS2.meta.add_dx_name_column()`
* `DHIS2.meta.add_coc_name_column()`
* `DHIS2.meta.add_org_unit_name_column()`

```python
>>> import polars as pl
>>> from openhexa.sdk import workspace
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion dans un espace de travail OpenHEXA
>>> con = workspace.dhis2_connection("DHIS2_PLAY")
>>> dhis = DHIS2(con, cache_dir=".cache")

>>> data_values = dhis.analytics.get(
...     data_elements=["V37YqbqpEhV", "tn3p7vIxoKY", "HZSdnO5fCUc"],
...     org_units=["JQr6TJx5KE3", "KbO0JnhiMwl", "f90eISKFm7P"],
...     periods=["202201", "202202", "202203"]
... )

>>> df = pl.DataFrame(data_values)
>>> df = dhis.meta.add_dx_name_column(df)
>>> print(df)

shape: (14, 6)
┌─────────────┬─────────────┬─────────────┬────────┬───────┬───────────────────────────┐
│ dx          ┆ co          ┆ ou          ┆ pe     ┆ value ┆ dx_name                   │
│ ---         ┆ ---         ┆ ---         ┆ ---    ┆ ---   ┆ ---                       │
│ str         ┆ str         ┆ str         ┆ str    ┆ str   ┆ str                       │
╞═════════════╪═════════════╪═════════════╪════════╪═══════╪═══════════════════════════╡
│ V37YqbqpEhV ┆ PT59n8BQbqM ┆ JQr6TJx5KE3 ┆ 202201 ┆ 5     ┆ IPT 2nd dose given at PHU │
│ V37YqbqpEhV ┆ pq2XI5kz2BY ┆ f90eISKFm7P ┆ 202201 ┆ 4     ┆ IPT 2nd dose given at PHU │
│ …           ┆ …           ┆ …           ┆ …      ┆ …     ┆ …                         │
└─────────────┴─────────────┴─────────────┴────────┴───────┴───────────────────────────┘
```

#### Pyramide

Une méthode utilitaire pour ajouter la pyramide complète des unités d'organisation à un dataframe est disponible sous le namespace `DHIS.meta` :

* `DHIS2.meta.add_org_unit_parent_columns()`

```python
>>> import polars as pl
>>> from openhexa.sdk import workspace
>>> from openhexa.toolbox.dhis2 import DHIS2

>>> # initialiser une nouvelle connexion dans un espace de travail OpenHEXA
>>> con = workspace.dhis2_connection("DHIS2_PLAY")
>>> dhis = DHIS2(con, cache_dir=".cache")

>>> data_values = dhis.analytics.get(
...     data_elements=["V37YqbqpEhV", "tn3p7vIxoKY", "HZSdnO5fCUc"],
...     org_units=["JQr6TJx5KE3", "KbO0JnhiMwl", "f90eISKFm7P"],
...     periods=["202201", "202202", "202203"]
... )

>>> df = pl.DataFrame(data_values)
>>> df = dhis.meta.add_org_unit_parent_columns(df)
>>> print(df)

shape: (14, 11)
┌────────────┬────────────┬───────────┬────────┬───┬───────────┬───────────┬───────────┬───────────┐
│ dx         ┆ co         ┆ ou        ┆ pe     ┆ … ┆ parent_le ┆ parent_le ┆ parent_le ┆ parent_le │
│ ---        ┆ ---        ┆ ---       ┆ ---    ┆   ┆ vel_2_id  ┆ vel_2_nam ┆ vel_3_id  ┆ vel_3_nam │
│ str        ┆ str        ┆ str       ┆ str    ┆   ┆ ---       ┆ e         ┆ ---       ┆ e         │
│            ┆            ┆           ┆        ┆   ┆ str       ┆ ---       ┆ str       ┆ ---       │
│            ┆            ┆           ┆        ┆   ┆           ┆ str       ┆           ┆ str       │
╞════════════╪════════════╪═══════════╪════════╪═══╪═══════════╪═══════════╪═══════════╪═══════════╡
│ V37YqbqpEh ┆ PT59n8BQbq ┆ JQr6TJx5K ┆ 202201 ┆ … ┆ jUb8gELQA ┆ Kailahun  ┆ cM2BKSrj9 ┆ Luawa     │
│ V          ┆ M          ┆ E3        ┆        ┆   ┆ pl        ┆           ┆ F9        ┆           │
│ …          ┆ …          ┆ …         ┆ …      ┆ … ┆ …         ┆ …         ┆ …         ┆ …         │
└────────────┴────────────┴───────────┴────────┴───┴───────────┴───────────┴───────────┴───────────┘
```

### Écrire des données

En cours de développement.

### Périodes

Des classes et méthodes utilitaires pour gérer les périodes DHIS2 sont disponibles dans le module `openhexa.toolbox.dhis2.periods`.

```python
>>> from openhexa.toolbox.dhis2.periods import Month, Quarter, period_from_string

>>> m1 = Month("202211")
>>> m2 = Month("202302")
>>> m2 > m1
True

>>> m1.get_range(m2)
["202211", "202212", "202301", "202302"]

>>> q1 = Quarter("2022Q3")
>>> q2 = Quarter("2023Q2")
>>> q1.get_range(q2)
["2022Q3", "2022Q4", "2023Q1", "2023Q2"]

>>> period_from_string("2022Q3") == q1
True
```



# OpenHEXA Toolbox IASO

Module pour récupérer des données depuis IASO.

## Installation

``` sh
pip install openhexa.toolbox
```

## Usage

### Connexion à une instance

Des identifiants sont requis pour initialiser une connexion à une instance IASO. Les identifiants doivent contenir le nom d'utilisateur et
le mot de passe pour se connecter à une instance d'IASO. Vous devez également fournir le nom d'hôte pour que l'API se connecte à :
* Environnement de staging https://iaso-staging.bluesquare.org/api
* Environnement de production https://iaso.bluesquare.org/api

Importez le module IASO comme suit :
```
from openhexa.toolbox.iaso import IASO

iaso = IASO("https://iaso-staging.bluesquare.org","username", "password")
```

### Lire les données

Après avoir importé le module IASO, vous pouvez utiliser la méthode fournie pour récupérer les Projects, Organisation Units et Forms pour lesquels vous avez
des permissions.
```
# Récupérer les projets
iaso.get_projects()
# Récupérer les unités d'organisation
iaso.get_org_units()
# Récupérer les formulaires soumis filtrés par form_ids passés dans les paramètres URL et avec le choix de les récupérer en dataframe
iaso.get_form_instances(page=1, limit=1, as_dataframe=True,
	dataframe_columns=["Date de création","Date de modification","Org unit"], ids=276)
# Récupérer les formulaires filtrés par unités d'organisation et projets pour lesquels vous avez des permissions
iaso.get_forms(org_units=[781], projects=[149])
```

Vous pouvez également fournir des paramètres supplémentaires à la méthode pour filtrer sur les valeurs souhaitées sous forme d'arguments key-value.
Vous pouvez avoir un aperçu des arguments sur lesquels filtrer dans la documentation API d'IASO.

# OpenHEXA Toolbox - Client OpenHEXA (n'est plus maintenu)

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
