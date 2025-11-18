<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Connexions</h1>
</div>
</div>

Les connexions sont des sources de données externes que vous utilisez au sein d'un espace de travail. Elles servent deux objectifs dans OpenHEXA :

1. Elles vous permettent de **stocker en toute sécurité les identifiants** pour les systèmes de données externes, afin de pouvoir les réutiliser dans les notebooks et les pipelines de données
2. Elles vous aident à **documenter** quelles sources de données vous utilisez au sein d'un espace de travail et comment vous les utilisez

![Connections](../assets/images/connections/connections.png)

!!! info "Permissions des connexions par rôle"
    - **Viewers** : Peuvent voir la liste des connexions mais ne peuvent pas les utiliser ou les gérer
    - **Editors** : Peuvent voir, utiliser les connexions dans les notebooks et les pipelines, mais ne peuvent pas créer ou supprimer des connexions
    - **Admins** : Peuvent voir, utiliser, créer, modifier et supprimer des connexions

Vous pouvez utiliser les connexions d'espace de travail dans les [notebooks OpenHEXA](notebooks.md) et les [pipelines de données OpenHEXA](pipelines.md).

OpenHEXA prend en charge les types de connexion suivants :

- PostgreSQL
- [DHIS2](https://dhis2.org/)
- [IASO](https://openiaso.com)
- S3 (Amazon Web Services)
- GCS (Google Cloud Platform)
- Personnalisé

## Utiliser les types de connexion intégrés

L'utilisation des types de connexion intégrés (PostgreSQL, DHIS2, S3 ou GCS) est simple. Vous devez simplement remplir le formulaire de création de connexion.

Ces types de connexion intégrés ont deux champs en commun :

- **Nom de connexion** : Le nom qu'OpenHEXA affiche sur l'écran des connexions. Vous pouvez choisir n'importe quel nom.
- **Description** : Optionnel. Utilisez-le pour documenter l'objectif de la source de données dans votre espace de travail.

Un identifiant unique est ajouté à la connexion en fonction du nom de la connexion.

## Utiliser des connexions personnalisées

Les connexions personnalisées sont utiles pour stocker des identifiants pour des systèmes qu'OpenHEXA ne prend pas en charge nativement.

Comme les connexions intégrées, les connexions personnalisées ont un nom et une description optionnelle. Vous pouvez ajouter autant de champs que vous le souhaitez à votre connexion personnalisée et les marquer comme secrets s'ils contiennent des informations sensibles (comme des mots de passe ou des jetons API).

