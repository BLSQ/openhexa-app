<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>L'IA dans OpenHEXA</h1>
</div>
</div>

OpenHEXA utilise des grands modèles de langage (LLM) à deux endroits : l'**assistant intégré**, qui vous aide à créer et modifier des pipelines, des webapps et des requêtes SQL depuis l'application, et le **serveur MCP**, qui permet à un client IA de votre choix (Claude, ChatGPT, Gemini CLI...) de travailler avec vos workspaces. Cette page explique ce que fait chacun d'eux, à quoi il a accès et quels modèles sont utilisés.

!!! warning "L'IA peut faire des erreurs"
    Le code, les requêtes et les réponses générés peuvent être faux, incomplets ou obsolètes. Relisez toujours ce que l'IA propose avant de l'accepter, de l'exécuter ou de le partager.

## Comment l'IA est utilisée

### L'assistant intégré

L'assistant est disponible dans les workspaces d'une organisation où un administrateur l'a activé (**Paramètres de l'organisation → Assistant IA**). Il apparaît à quelques endroits précis, chacun avec une tâche étroitement délimitée :

| Où | Ce qu'il fait |
| --- | --- |
| **Pipelines → Créer → Créer avec l'IA** | Transforme votre description en un nouveau pipeline avec une première version de son code. |
| **Éditeur de code d'un pipeline → panneau de chat** | Lit les fichiers du pipeline et propose une nouvelle version. Rien n'est enregistré tant que vous n'avez pas relu et accepté la proposition. |
| **Web Apps → Créer → Créer avec l'IA** | Crée une webapp statique à partir de votre description, puis l'ouvre dans l'éditeur de code. |
| **Éditeur de code d'une webapp → panneau de chat** | Lit les fichiers de la webapp et propose une nouvelle version, que vous relisez et acceptez. |
| **Data Studio → Générer du SQL** | Traduit une question en une seule requête `SELECT` en lecture seule. Le modèle ne voit que la structure de la base de données (noms et types des tables et des colonnes), jamais les données contenues dans les tables. Avant d'être affichée, la requête est seulement planifiée par la base de données pour détecter les erreurs, pas exécutée. Elle ne s'exécute que lorsque vous la lancez. |

Un petit modèle donne également un titre court à chaque conversation.

L'assistant fonctionne avec un jeu d'instructions fixe pour chaque tâche et décline les demandes sans rapport avec OpenHEXA. Il ne peut pas exécuter de pipelines, lancer du SQL de sa propre initiative, modifier des permissions ni agir en dehors du workspace de la conversation.

Chaque utilisateur dispose d'un budget d'utilisation mensuel fixé par l'instance. Lorsqu'il est atteint, l'assistant est suspendu jusqu'au mois suivant.

### Le serveur MCP

OpenHEXA expose un serveur [Model Context Protocol (MCP)](https://modelcontextprotocol.io) pour que des assistants IA externes puissent lister, lire et agir sur vos workspaces. Les instructions de configuration des clients pris en charge se trouvent à l'adresse `/mcp/wiki` de votre instance OpenHEXA (par exemple <https://app.openhexa.org/mcp/wiki>), et le catalogue complet des outils à `/mcp`.

La connexion d'un client passe par OAuth : le client vous renvoie vers OpenHEXA, où vous vous connectez et choisissez les workspaces auxquels il peut accéder et les outils qu'il peut appeler. Vous pouvez restreindre ou révoquer ces autorisations à tout moment depuis **Compte → Connexions MCP**. Les changements s'appliquent au prochain appel.

Avec MCP, le modèle est celui de votre client IA, pas celui d'OpenHEXA. Tout ce qu'un outil renvoie (contenu de fichiers, aperçus de jeux de données, code de pipelines...) est envoyé à ce client et traité par son fournisseur selon ses propres conditions : n'accordez donc que les workspaces et les outils dont vous avez réellement besoin.

## À quoi l'IA a accès

Dans les deux cas, l'IA agit **en votre nom** : chaque appel d'outil passe par les mêmes vérifications de permissions que l'interface OpenHEXA, de sorte que l'IA ne peut jamais voir ni faire plus que votre propre compte. Une connexion MCP est de plus limitée aux workspaces et aux outils que vous lui avez accordés.

### Assistant intégré

| Tâche | Lit | Écrit |
| --- | --- | --- |
| Créer / modifier un pipeline | Les métadonnées et la description du workspace, les jeux de données et les aperçus de leurs fichiers, les fichiers du workspace, les noms des connexions et de leurs champs (jamais les valeurs secrètes), le code et les fichiers du pipeline lui-même, la documentation OpenHEXA | Crée le pipeline (création) ; propose une nouvelle version que vous acceptez (modification) |
| Créer / modifier une webapp | Comme pour les pipelines, plus le schéma de la base de données (tables et colonnes, pas les lignes), les requêtes enregistrées, la liste des pipelines et les fichiers de la webapp | Crée la webapp ; crée ou met à jour des requêtes enregistrées ; propose une nouvelle version que vous acceptez |
| Générer du SQL | Uniquement le schéma de la base de données : noms et types des tables et des colonnes. Il ne lit jamais les lignes d'une table, et aucun résultat de requête n'est envoyé au modèle | Rien : la requête vous est seulement affichée |

Si le workspace a une description, elle est fournie à l'assistant comme contexte. Les administrateurs du workspace peuvent s'en servir pour documenter les conventions de données, mais l'assistant la traite comme de l'information, pas comme des instructions.

### Serveur MCP

Les outils sont regroupés par ressource. Chaque autorisation couvre un groupe, les outils de lecture et d'écriture étant accordés séparément :

| Ressource | Outils de lecture | Outils d'écriture |
| --- | --- | --- |
| Workspaces | lister, consulter | mettre à jour |
| Fichiers | lister, lire | écrire |
| Jeux de données | lister, consulter, prévisualiser les fichiers | créer des jeux de données et des versions |
| Pipelines | lister, consulter, consulter une exécution | exécuter, mettre à jour, créer, créer une version |
| Modèles de pipelines | lister, consulter | créer un pipeline à partir d'un modèle |
| Webapps | lister, consulter, lire les fichiers | créer, mettre à jour, modifier les fichiers |
| Bases de données | schéma des tables et colonnes (pas les lignes) | — |
| Requêtes enregistrées | lister, consulter le SQL | créer, mettre à jour |
| Connexions | lister les noms, types et noms de champs (pas les valeurs secrètes) | — |

Seul l'outil d'aide, qui renvoie la documentation OpenHEXA, fonctionne sans autorisation. Aucun outil MCP n'exécute de SQL sur une base de données de workspace ni ne renvoie de secrets de connexion.

## Modèles

!!! info "Ceci évoluera avec le temps"
    Les modèles évoluent vite. Ceux ci-dessous sont utilisés au moment de la rédaction ; OpenHEXA les met à jour à mesure que de meilleurs modèles, ou des modèles moins chers, deviennent disponibles, sans changer le fonctionnement de l'assistant. Consultez les [notes de version](https://github.com/BLSQ/openhexa-app/blob/main/CHANGELOG.md) pour les derniers changements.

- **Instances gérées** (hébergées par Bluesquare) : l'assistant utilise les modèles Claude d'Anthropic servis via Google Cloud Vertex AI plutôt que par l'API d'Anthropic. Les requêtes sont traitées dans la région Google `europe-west1`, à Saint-Ghislain en Belgique : vos données restent dans l'UE et sont couvertes par les conditions de traitement des données RGPD de Google Cloud. Google n'utilise pas vos données pour entraîner des modèles et ne les partage pas avec Anthropic. L'assistant tourne sur Claude Opus 4.6 et les titres de conversation sur Claude Haiku 4.5. Les opérateurs peuvent diriger certaines tâches vers d'autres modèles disponibles sur Vertex AI.
- **Instances auto-hébergées** : chaque organisation fournit sa propre clé API Anthropic et choisit Claude Haiku 4.5, Sonnet 4.6 ou Opus 4.6 dans **Paramètres de l'organisation → Assistant IA**. Les requêtes vont directement chez Anthropic, dans le cadre de l'accord propre à l'organisation.
- **MCP** : le modèle utilisé par votre client IA.

## Ce qui est conservé

Pour l'assistant intégré, OpenHEXA conserve vos conversations : vos messages, les réponses de l'assistant, chaque appel d'outil avec son entrée et sa sortie, le nombre de tokens et le coût qui en résulte. Elles sont liées à votre compte et au workspace, et les administrateurs de l'instance peuvent les consulter pour le support et le suivi des coûts. Pour MCP, OpenHEXA journalise chaque appel d'outil (nom de l'outil, arguments, succès ou erreur) et la date de dernière utilisation de chaque connexion.

Vos messages et le contexte décrit ci-dessus sont envoyés au fournisseur du modèle pour produire une réponse. Évitez d'y mettre des données personnelles, des identifiants ou d'autres informations sensibles.

## Utiliser l'IA de manière responsable

- Relisez chaque changement proposé avant de l'accepter, et lisez le SQL généré avant de l'exécuter.
- Gardez une personne dans la boucle pour les décisions qui concernent des personnes ou des données de production.
- N'accordez aux clients MCP que les workspaces et les outils dont ils ont besoin, et révoquez les connexions que vous n'utilisez plus.
- Signalez tout comportement erroné ou surprenant à votre administrateur ou sur [GitHub](https://github.com/BLSQ/openhexa/issues).
