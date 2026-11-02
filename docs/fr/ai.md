<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>L'IA dans OpenHEXA</h1>
</div>
</div>

OpenHEXA intègre des grands modèles de langage (LLM) de deux manières : via l'**assistant intégré**, qui vous aide à créer et modifier des pipelines, des applications web et des requêtes SQL directement depuis la plateforme, et via un **serveur MCP**, qui permet au client IA de votre choix (Claude, ChatGPT, Gemini CLI...) d'interagir avec vos workspaces. Cette page explique le rôle de chaque intégration, les données auxquelles elle a accès et les modèles utilisés.

!!! warning "L'IA peut faire des erreurs"
    Le code, les requêtes et les réponses générés peuvent comporter des erreurs, être incomplets ou obsolètes. Vérifiez toujours ce que l'IA propose avant de l'accepter, de l'exécuter ou de le partager.

## Comment l'IA est utilisée

### L'assistant intégré

L'assistant est disponible dans les workspaces d'une organisation dès lors qu'un administrateur l'a activé (**Paramètres de l'organisation → Assistant IA**). Il intervient pour des tâches précises et bien délimitées à quelques endroits clés :

| Emplacement | Ce qu'il fait |
| --- | --- |
| **Pipelines → Créer → Créer avec l'IA** | Génère un nouveau pipeline ainsi que la première version de son code à partir de votre description. |
| **Éditeur de code d'un pipeline → panneau de discussion** | Lit les fichiers du pipeline et propose des modifications ou une nouvelle version. Rien n'est enregistré tant que vous n'avez pas relu et accepté la proposition. |
| **Web Apps → Créer → Créer avec l'IA** | Crée une application web statique à partir de votre description, puis l'ouvre dans l'éditeur de code. |
| **Éditeur de code d'une webapp → panneau de discussion** | Lit les fichiers de l'application web et propose des modifications, que vous pouvez relire et accepter avant enregistrement. |
| **Data Studio → Générer du SQL** | Traduit une question en langage naturel en une unique requête `SELECT` en lecture seule. Le modèle ne voit que le schéma de la base de données (noms et types des tables et des colonnes), jamais les données des tables. Avant d'être affichée, la requête est simplement planifiée par la base de données pour détecter d'éventuelles erreurs de syntaxe, sans être exécutée. Elle n'est exécutée que lorsque vous choisissez de la lancer. |

Un modèle léger attribue également un titre court et automatique à chaque conversation.

L'assistant fonctionne avec des consignes dédiées pour chaque tâche et décline les demandes sans rapport avec OpenHEXA. Il ne peut pas lancer de pipelines, exécuter de requêtes SQL de sa propre initiative, modifier des permissions ni agir en dehors du workspace actif.

Sur la plateforme hébergée, chaque organisation dispose d'un budget IA mensuel fixé par son abonnement. Une fois ce budget atteint, les fonctionnalités IA sont suspendues pour toute l'organisation jusqu'au début du mois suivant. Les instances auto-hébergées n'ont pas de budget intégré : les dépenses ne sont limitées que par les plafonds configurés chez votre fournisseur d'IA.

### Le serveur MCP

OpenHEXA met à disposition un serveur [Model Context Protocol (MCP)](https://modelcontextprotocol.io) permettant à des assistants IA externes d'explorer vos workspaces et d'interagir avec eux. Les instructions de configuration pour les clients pris en charge sont disponibles à l'adresse `/mcp/wiki` sur votre instance OpenHEXA (par exemple <https://app.openhexa.org/mcp/wiki>), et le catalogue complet des outils se trouve sur `/mcp`.

La connexion d'un client s'effectue via OAuth : le client vous redirige vers OpenHEXA, où vous vous connectez pour sélectionner précisément les workspaces accessibles et les outils autorisés. Les workspaces sont regroupés par organisation : sélectionner une organisation donne accès à tous ses workspaces, y compris ceux créés ou rejoints par la suite. Vous pouvez restreindre ou révoquer ces autorisations à tout moment depuis **Compte → Connexions MCP**. Les modifications prennent effet dès l'appel d'outil suivant.

Avec MCP, le modèle utilisé est celui de votre client IA, et non celui d'OpenHEXA. Toutes les données renvoyées par un outil (contenu de fichiers, aperçus de jeux de données, code de pipelines...) sont transmises à ce client et traitées selon les conditions de son fournisseur. N'accordez donc l'accès qu'aux workspaces et aux outils dont vous avez réellement besoin.

## Données et ressources accessibles par l'IA

Dans les deux cas, l'IA agit **en votre nom** : chaque appel d'outil passe par les mêmes vérifications de permissions que l'interface OpenHEXA. L'IA ne peut donc jamais voir ni modifier plus que ce que votre propre compte autorise. Une connexion MCP est en outre limitée aux workspaces et aux outils que vous lui avez expressément accordés.

### Assistant intégré

| Tâche | Données lues | Données écrites |
| --- | --- | --- |
| Créer / modifier un pipeline | Métadonnées et description du workspace, jeux de données et aperçus de leurs fichiers, fichiers du workspace, noms des connexions et de leurs champs (jamais les valeurs secrètes), code et fichiers du pipeline, documentation OpenHEXA | Crée le pipeline (création) ; propose des modifications ou une nouvelle version à valider (modification) |
| Créer / modifier une webapp | Identique aux pipelines, plus le schéma de la base de données (tables et colonnes, jamais les lignes), les requêtes enregistrées, la liste des pipelines et les fichiers de l'application web | Crée l'application web ; crée ou met à jour des requêtes enregistrées ; propose des modifications à valider |
| Générer du SQL | Uniquement le schéma de la base de données (noms et types des tables et des colonnes). Elle ne lit jamais les lignes des tables, et aucun résultat de requête n'est envoyé au modèle | Rien : la requête est seulement affichée pour relecture |

Si le workspace possède une description, celle-ci est fournie à l'assistant comme contexte. Les administrateurs du workspace peuvent s'en servir pour documenter les conventions de données, mais l'assistant la traite comme un élément informatif, et non comme une instruction pouvant outrepasser ses règles.

### Serveur MCP

Les outils sont regroupés par type de ressource. Chaque autorisation couvre un groupe, les outils de lecture et d'écriture étant accordés séparément :

| Ressource | Outils de lecture | Outils d'écriture |
| --- | --- | --- |
| Workspaces | lister, consulter | mettre à jour |
| Fichiers | lister, lire | écrire |
| Jeux de données | lister, consulter, prévisualiser les fichiers | créer des jeux de données et des versions |
| Pipelines | lister, consulter, consulter une exécution | exécuter, mettre à jour, créer, créer une version |
| Modèles de pipelines | lister, consulter | créer un pipeline à partir d'un modèle |
| Webapps | lister, consulter, lire les fichiers | créer, mettre à jour, modifier les fichiers |
| Bases de données | schéma des tables et colonnes (jamais les lignes) | — |
| Requêtes enregistrées | lister, consulter le SQL | créer, mettre à jour |
| Connexions | lister les noms, types et noms de champs (jamais les valeurs secrètes) | — |

Seul l'outil d'aide, qui renvoie la documentation OpenHEXA, fonctionne sans autorisation préalable. Aucun outil MCP n'exécute de requête SQL sur une base de données de workspace ni ne renvoie de secrets de connexion.

## Modèles

!!! info "Les modèles évoluent avec le temps"
    Les modèles de langage évoluent rapidement. Ceux mentionnés ci-dessous sont utilisés au moment de la rédaction ; OpenHEXA les met à jour à mesure que des modèles plus performants ou plus économiques deviennent disponibles, sans modifier le fonctionnement de l'assistant. Consultez les [notes de version](https://github.com/BLSQ/openhexa-app/blob/main/CHANGELOG.md) pour suivre les dernières nouveautés.

- **Instances gérées** (hébergées par Bluesquare) : l'assistant utilise les modèles Claude d'Anthropic servis via Google Cloud Vertex AI plutôt que par l'API directe d'Anthropic. Les requêtes sont traitées dans la région Google `europe-west1`, à Saint-Ghislain en Belgique : vos données restent dans l'UE et bénéficient des conditions de traitement des données RGPD de Google Cloud. Google n'utilise pas vos données pour entraîner ses modèles et ne les partage pas avec Anthropic. L'assistant repose sur Claude Opus 4.6, et les titres de conversation sur Claude Haiku 4.5. Les administrateurs de l'instance peuvent orienter certaines tâches vers d'autres modèles disponibles sur Vertex AI.
- **Instances auto-hébergées** : chaque organisation fournit sa propre clé API Anthropic et choisit Claude Haiku 4.5, Sonnet 4.6 ou Opus 4.6 dans **Paramètres de l'organisation → Assistant IA**. Les requêtes sont envoyées directement à Anthropic dans le cadre des conditions contractuelles propres à l'organisation.
- **MCP** : le modèle dépend entièrement du client IA que vous connectez.

## Ce qui est conservé

Pour l'assistant intégré, OpenHEXA conserve vos conversations : vos messages, les réponses de l'assistant, chaque appel d'outil ainsi que ses entrées et sorties, le nombre de tokens et le coût associé. Ces données sont associées à votre compte et au workspace ; les administrateurs de l'instance peuvent les consulter pour le support technique et le suivi des coûts. Pour MCP, OpenHEXA journalise chaque appel d'outil (nom de l'outil, arguments, statut de réussite ou d'erreur) et enregistre la date de dernière utilisation de chaque connexion.

Vos messages et le contexte décrit plus haut sont transmis au fournisseur du modèle pour générer les réponses. Évitez d'inclure des données personnelles, des identifiants ou toute autre information sensible dans vos messages.

## Utiliser l'IA de manière responsable

- Relisez attentivement chaque modification proposée avant de l'accepter, et examinez le SQL généré avant de l'exécuter.
- Conservez une supervision humaine pour toute décision ayant un impact sur des personnes ou sur des données de production.
- N'accordez aux clients MCP que l'accès aux workspaces et aux outils strictement nécessaires, et révoquez les connexions inutilisées.
- Signalez tout comportement erroné, inattendu ou surprenant à votre administrateur ou sur [GitHub](https://github.com/BLSQ/openhexa/issues).
