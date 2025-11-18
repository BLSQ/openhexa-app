<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Espaces de travail</h1>
</div>
</div>


## Contexte d'espace de travail

Lorsque vous avez accès à plusieurs espaces de travail, vous pouvez facilement basculer entre eux en utilisant le menu de sélection d'espace de travail dans le coin supérieur gauche de l'écran. Ce menu déroulant vous permet de naviguer rapidement entre tous les espaces de travail où vous avez accès.

![Workspace Switcher](../assets/images/workspaces/workspace_switcher.png)



## Créer de nouveaux espaces de travail

Vous pouvez créer de nouveaux espaces de travail si vous êtes :

- **Admin ou Owner de l'organisation** : Cliquez sur le bouton ⊕ dans le menu de sélection d'espace de travail
- **Admin d'espace de travail** : Les utilisateurs qui sont Admins d'au moins un espace de travail existant peuvent également créer de nouveaux espaces de travail

## Page d'accueil de l'espace de travail

Vous pouvez utiliser la page d'accueil de l'espace de travail pour expliquer l'objectif de l'espace de travail, documenter les données et les processus de l'espace de travail, ou ajouter des liens utiles vers des ressources externes. 

![Workspace Home](../assets/images/workspaces/home.png){ width="70%" }

Si vous avez le rôle **Editor** ou **Admin** dans l'espace de travail, vous pouvez modifier le contenu de la page d'accueil en cliquant sur **Modifier**. 

## Configuration générale

Si vous êtes un Admin d'espace de travail, vous pouvez utiliser l'option **Administration** pour gérer votre espace de travail.

![Workspace Admin Access](../assets/images/workspaces/workspace_admin.png)

Dans la configuration générale, vous pouvez changer le nom de l'espace de travail et définir les pays associés. Ces paramètres aident à identifier votre espace de travail sur la plateforme.

![Workspace general settings](../assets/images/workspaces/workspace_general.png)

### Configuration de l'image Docker

Toute exécution de code dans OpenHEXA (pipelines, notebooks, etc.) se déroule dans des conteneurs Docker. Chaque espace de travail peut spécifier une image Docker personnalisée qui définit l'environnement d'exécution, y compris les packages et dépendances pré-installés.

Le paramètre d'image de l'espace de travail vous permet de sélectionner quelle image Docker sera utilisée comme environnement d'exécution. L'ID d'image spécifié sera récupéré depuis le dépôt Docker Hub de Bluesquare.

!!! info "Images personnalisées"
    Pour demander une image Docker personnalisée pour votre espace de travail :
    
    1. Contactez l'équipe OpenHEXA avec vos exigences :
       - E-mail : openhexa@bluesquarehub.com
       - Incluez des détails sur les packages et dépendances requis
    2. Nous créerons et publierons une image optimisée.
    3. Vous pourrez ensuite la sélectionner dans les paramètres de votre espace de travail.
    
    À l'avenir, nous prévoyons de fournir davantage d'options en libre-service pour la personnalisation des images.

!!! tip "Image par défaut"
    Si vous ne spécifiez pas d'image personnalisée, l'espace de travail utilise l'image OpenHEXA standard, qui inclut des packages courants de data science comme pandas, numpy, scikit-learn, et plus encore.

![Workspace image settings](../assets/images/workspaces/workspace_image.png)

### Configuration de l'espace de travail
En tant qu'Admin d'espace de travail, vous pouvez définir des propriétés de configuration : **paires clé-valeur nommées** que vos notebooks et pipelines peuvent lire avec le SDK OpenHEXA pour contrôler le comportement à l'exécution (par exemple, activer/désactiver des fonctionnalités, définir des paramètres par défaut, ou pointer vers des ressources externes). Cela vous permet d'adapter la logique par espace de travail sans modifier le code.

Les utilisations typiques incluent :

- Indicateurs de fonctionnalités (activer ou désactiver des capacités par espace de travail)
- Paramètres par défaut (par exemple, ID de jeux de données ou codes de pays par défaut)
- URL externes ou identifiants utilisés par les tâches

!!! warning "Utiliser uniquement pour la configuration"
    Stockez les secrets et les identifiants dans la fonctionnalité dédiée [Connexions](connections.md) plutôt que dans les propriétés de configuration.


![Workspace configuration properties](../assets/images/workspaces/workspace_configuration.png)

## Membres
### Ajouter ou inviter des membres
En tant qu'**Admin** d'espace de travail, vous pouvez inviter des utilisateurs à rejoindre votre espace de travail. Vous pouvez inviter à la fois des utilisateurs OpenHEXA existants (qui peuvent travailler dans d'autres espaces de travail) et de nouveaux utilisateurs qui n'ont pas encore utilisé la plateforme.

Pour inviter des utilisateurs :

- **Pour les utilisateurs existants** : Recherchez par leur nom.
- **Pour les nouveaux utilisateurs** : Entrez leur adresse e-mail.
- Sélectionnez leur rôle dans l'espace de travail (**Admin**, **Editor** ou **Viewer**).

Les utilisateurs invités recevront une invitation par e-mail pour rejoindre l'espace de travail, que vous verrez dans la section **Invitations en attente et refusées**. Une fois qu'ils acceptent, ils auront accès selon leur rôle assigné.


### Rôles et permissions

Le rôle d'un utilisateur détermine les actions qu'il peut effectuer au sein d'un espace de travail. Chaque section de ce manuel d'utilisation inclut des informations spécifiques aux rôles pour vous aider à comprendre quelles actions vous sont disponibles.

Le tableau suivant résume les permissions pour chaque rôle :

|| Fonctionnalités | Viewers | Editors | Admins |
|----------|---------|---------|--------|
|| Lire et télécharger des fichiers | ✅ | ✅ | ✅ |
|| Écrire des fichiers | ❌ | ✅ | ✅ |
|| Voir le contenu de la base de données | ✅ | ✅ | ✅ |
|| Voir les identifiants de la base de données | ❌ | ✅ | ✅ |
|| Écrire dans la base de données | ❌ | ✅ | ✅ |
|| Régénérer le mot de passe de la base de données | ❌ | ❌ | ✅ |
|| Lire et télécharger les jeux de données | ✅ | ✅ | ✅ |
|| Écrire des jeux de données | ❌ | ✅ | ✅ |
|| Utiliser les connexions | ❌ | ✅ | ✅ |
|| Gérer les connexions | ❌ | ❌ | ✅ |
|| Lancer des pipelines | ✅ | ✅ | ✅ |
|| Créer des pipelines | ❌ | ✅ | ✅ |
|| Utiliser les notebooks | ❌ | ✅ | ✅ |
|| Mettre à jour la description de l'espace de travail | ❌ | ✅ | ✅ |
|| Gérer et inviter des utilisateurs | ❌ | ❌ | ✅ |


## Base de données
### Régénérer le mot de passe de la base de données de l'espace de travail

Lorsque vous créez un espace de travail, une **base de données relationnelle est automatiquement provisionnée** avec un nom d'utilisateur et un mot de passe.

Si le mot de passe est compromis, vous pouvez l'invalider et en créer un nouveau dans la section des paramètres.


## Archive
Les Admins peuvent également archiver l'espace de travail. Cliquez sur **Archiver**.

