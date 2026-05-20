<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Utiliser l'OpenHEXA CLI</h1>
</div>
</div>

OpenHEXA est livré avec une CLI que vous pouvez installer globalement sur votre système. Cette CLI vous permet d'interagir avec l'API OpenHEXA et d'effectuer diverses tâches telles que la création et la gestion de pipelines, l'exécution de tâches locales et plus encore.

## Installation

Pour installer la CLI, vous devez avoir `Python >3.9` et `pip` installés sur votre système. Vous pouvez ensuite installer la CLI à l'aide de la commande suivante :

```bash
python -m pip install openhexa.sdk
```

Vous pouvez ensuite exécuter la CLI à l'aide de la commande `openhexa`.

```bash
openhexa --help
```

## Configuration

Par défaut, la CLI cherche un fichier de configuration dans `~/.openhexa.ini`. Vous pouvez interagir avec la configuration à l'aide de la commande `openhexa config`.
La CLI est préconfigurée pour utiliser `https://api.openhexa.org` comme point de terminaison de l'API. Vous pouvez modifier cela en exécutant :

```bash
openhexa config set_url <my-endpoint-url>
```

Si vous avez besoin de plus d'informations sur la CLI, vous pouvez utiliser le drapeau `--help` pour obtenir plus d'informations sur les commandes et leurs options.

```bash
openhexa --help
openhexa workspaces --help
openhexa pipelines init --help
```

Si vous rencontrez des erreurs de vérification SSL, vous pouvez désactiver la vérification SSL (activée par défaut) avec le paramètre suivant :

```bash
export HEXA_VERIFY_SSL=false
```

Notez que vous ne devez l'utiliser que lorsque c'est vraiment nécessaire pour interagir avec des installations locales d'OpenHEXA. Cela peut être requis par exemple lorsqu'il manque la chaîne complète dans le certificat SSL.

## Gestion des espaces de travail

La CLI doit être configurée avec les espaces de travail avec lesquels vous souhaitez interagir. Vous pouvez ajouter, supprimer et lister des espaces de travail à l'aide de la commande `openhexa workspaces`.

### Ajouter un espace de travail

Pour ajouter un espace de travail à la configuration, vous pouvez exécuter :

```bash
openhexa workspaces add <workspace-slug>
```

La CLI vous demandera de fournir la clé API nécessaire pour cet espace de travail. Cette clé API peut être trouvée dans l'interface web OpenHEXA sur la page des pipelines. L'espace de travail nouvellement ajouté sera défini comme l'espace de travail actif.

Note : La CLI a besoin d'une clé API valide par espace de travail.

### Activer un espace de travail

Vous pouvez activer un espace de travail avec la commande `openhexa workspaces activate <workspace-slug>`. Cela définira l'espace de travail actif pour la CLI. Toutes les autres commandes CLI utiliseront cet espace de travail comme valeur par défaut. Vous pouvez consulter la liste des espaces de travail ajoutés avec la commande `openhexa workspaces list`.

## Pipelines

Vous pouvez lister, créer, mettre à jour, télécharger, exécuter et supprimer des pipelines à l'aide de la commande `openhexa pipelines`.

### Lister les pipelines

Vous pouvez lister les pipelines de l'espace de travail actif à l'aide de la commande `openhexa pipelines list`.

### Créer un pipeline

Vous pouvez créer un pipeline à l'aide de la commande `openhexa pipelines init <pipeline-name>`. Cela créera un nouveau répertoire portant le nom du pipeline et un fichier `pipeline.py`. Vous pouvez ensuite modifier ce fichier pour définir votre pipeline. Vous pouvez ensuite exécuter le pipeline à l'aide de la commande `openhexa pipelines run <pipeline-name>`.

L'approche recommandée est d'avoir un pipeline par dépôt git. Cela vous permet de versionner votre pipeline et de le partager avec d'autres. Lors de la création du pipeline, la CLI vous demandera si vous souhaitez créer un workflow GitHub pour pousser automatiquement votre pipeline vers OpenHEXA en fonction d'un tag git, d'un push sur `main` ou d'une action manuelle via l'interface GitHub.

Lors de l'envoi d'un pipeline, vous pouvez optionnellement spécifier :
- **Type fonctionnel** avec `-ft` ou `--functional-type` : Catégorisez votre pipeline comme `extraction`, `transformation`, `loading` ou `computation`
- **Tags** avec `-t` ou `--tag` : Ajoutez plusieurs tags pour organiser et filtrer les pipelines (peut être utilisé plusieurs fois)

Exemple :
```bash
openhexa pipelines push ./my-pipeline -ft extraction -t data-quality -t covid19
```


### Exécuter un pipeline

Les pipelines peuvent être exécutés localement avec [Docker](https://www.docker.com/products/docker-desktop/). Docker doit être installé sur votre système pour exécuter des pipelines.

Vous pouvez exécuter un pipeline avec la commande `openhexa pipelines run <pipeline-path>`. Si votre pipeline nécessite des paramètres, vous pouvez les passer via un fichier de configuration ou directement sous forme de chaîne JSON.

Sous forme de chaîne JSON :
```bash
openhexa pipelines run <pipeline-path> -c '{"param1": "value1", "param2": "value2"}'
```

Sous forme de fichier de configuration :
```bash
echo '{"param1": "value1", "param2": "value2"}' > ./config.json
openhexa pipelines run <pipeline-path> -f ./config.json
```

Si vous souhaitez que votre pipeline s'exécute avec une image différente de celle par défaut (`blsq/openhexa-blsq-environment:latest`), vous pouvez utiliser le drapeau `--image` pour spécifier l'image à utiliser.

```bash
openhexa pipelines run <pipeline-path> --image <image-name>
```

### Mettre à jour un pipeline

Vous pouvez mettre à jour un pipeline avec la commande `openhexa pipelines push <pipeline-path>`. Cela mettra à jour le pipeline dans l'API OpenHEXA avec la nouvelle définition du pipeline.

La commande `push` prend en charge plusieurs options :
- `-c, --code` : Spécifier le code du pipeline à mettre à jour
- `-n, --name` : Définir le nom de la version
- `-d, --description` : Ajouter une description de la version
- `-l, --link` : Fournir un lien vers le commit de la version
- `-ft, --functional-type` : Définir le type fonctionnel (`extraction`, `transformation`, `loading` ou `computation`)
- `-t, --tag` : Ajouter des tags (peut être utilisé plusieurs fois pour plusieurs tags)
- `--yes` : Ignorer les invites de confirmation (utile pour CI/CD)

### Télécharger un pipeline

Vous pouvez télécharger un pipeline avec la commande `openhexa pipelines download <pipeline-slug> <path>`. Cela téléchargera le pipeline vers le `path` indiqué. Si le chemin n'est pas vide, la CLI vous demandera si vous souhaitez écraser les fichiers existants.

### Supprimer un pipeline

Vous pouvez supprimer un pipeline avec la commande `openhexa pipelines delete <pipeline-slug>`. Cela supprimera le pipeline de l'API OpenHEXA.


## FAQ

### Comment obtenir la clé API d'un espace de travail ?

Vous pouvez trouver la clé API d'un espace de travail dans l'interface web OpenHEXA sur la page des pipelines en cliquant sur "+". Vous devez être au moins éditeur de l'espace de travail. La clé API est un secret et doit être conservée en lieu sûr. La CLI vous demandera de fournir la clé API lors de l'ajout d'un espace de travail.

### Comment obtenir le slug de l'espace de travail ?

Vous pouvez trouver le slug de l'espace de travail dans l'interface web OpenHEXA sur la page des pipelines. Le slug de l'espace de travail est la partie de l'URL après `https://app.openhexa.com/workspaces/<workspace-slug>/`.

### Comment obtenir le slug du pipeline ?

Vous pouvez trouver le slug du pipeline dans l'interface web OpenHEXA sur la page de chaque pipeline.

### J'obtiens des erreurs SSL en essayant d'ajouter un espace de travail.

Vous pouvez [désactiver la vérification SSL](#configuration) si nécessaire pour interagir avec le serveur.
