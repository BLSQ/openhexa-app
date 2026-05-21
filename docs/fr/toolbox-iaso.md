<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>OpenHEXA Toolbox IASO</h1>
</div>

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
