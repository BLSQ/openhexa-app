<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Utiliser OpenHEXA (version héritée)</h1>
</div>
</div>

!!! warning "Documentation héritée"
    Cette page documente l'ancienne interface OpenHEXA. Pour la plateforme actuelle, consultez le [Manuel d'utilisation](index.md).

## Premiers pas

Une fois que vous ou quelqu'un de votre organisation a terminé le [processus d'installation](installation.md), vous devez compléter quelques étapes simples avant de pouvoir utiliser OpenHEXA :

1. Créer une équipe
1. Inviter quelques utilisateurs
1. Ajouter vos premières sources de données

Passons en revue le processus.

### Créer une équipe

Tout d'abord, connectez-vous en tant qu'utilisateur root créé pendant le processus d'installation.

Ensuite, connectez-vous à OpenHEXA et, à l'aide du menu déroulant utilisateur, accédez à la section Admin.

<img width="600" alt="go_to_admin" src="https://user-images.githubusercontent.com/690667/192486908-08c32cdf-6f4c-4b45-ba1f-50232e8b0734.png">

Vous pouvez ensuite accéder à la section `User management > Teams` et ajouter une nouvelle équipe :

<img width="600" alt="create_team" src="https://user-images.githubusercontent.com/690667/192489032-f8e634d9-51dd-4391-a148-89fbe53a8402.png">

Vous n'avez besoin que de fournir un nom pour le moment, vous attribuerez les utilisateurs à l'équipe ultérieurement.

### Inviter des utilisateurs

Maintenant que votre équipe est créée, vous pouvez inviter des utilisateurs. Allez simplement dans la section `User management > Users` du panneau d'administration et ajoutez un utilisateur :

<img width="600" alt="Screenshot 2022-09-27 at 13 04 44" src="https://user-images.githubusercontent.com/690667/192509365-90d37c52-426c-4f36-91be-bbc40799ea9e.png">

À cette étape, sauf si vous avez vraiment besoin de choisir le mot de passe vous-même, vous devriez ignorer le formulaire de mot de passe : lorsque vous soumettez le formulaire de création d'utilisateur, le système enverra un email d'invitation à l'utilisateur contenant un lien lui permettant de choisir son propre mot de passe.

### Ajouter une première source de données

Maintenant que nous avons une équipe et quelques utilisateurs, ajoutons une source de données. Nous utiliserons le connecteur DHIS2 comme exemple, le processus est presque identique pour les autres sources de données. Nous utiliserons l'[instance de démonstration officielle DHIS2](https://play.dhis2.org/).

Le processus est le suivant :

Tout d'abord, allez dans `DHIS2 connector > DHIS2 API Credentials` dans le panneau d'administration et cliquez sur `Add DHIS2 API Credentials`.

<img width="600" alt="Screenshot 2022-09-27 at 14 16 00" src="https://user-images.githubusercontent.com/690667/192524122-d15c2754-f0e2-4a47-892c-97aefd40866d.png">

Après avoir enregistré les identifiants, allez dans `DHIS2 connector > DHIS2 Instances` et cliquez sur `Add DHIS2 instance`.

<img width="600" alt="Screenshot 2022-09-27 at 14 21 06" src="https://user-images.githubusercontent.com/690667/192525063-257b2fc7-69c0-4bdb-8fe0-494939fd6fa7.png">

Il vous suffit de sélectionner les identifiants API créés ci-dessus, de fournir l'URL de l'API et un nom pour l'instance. Enregistrez le formulaire et c'est terminé : vous avez ajouté vos premières sources de données dans OpenHEXA.

Vous voudrez peut-être ajouter d'autres sources de données à ce stade, par exemple un bucket AWS S3 — le processus est presque le même que pour une instance DHIS2, à l'exception de la partie identifiants.

## Utiliser le catalogue

Le **catalogue de données** peut être utilisé pour explorer et rechercher des données dans vos sources de données.

### Explorer les données

Allez simplement à l'interface principale OpenHEXA (c'est-à-dire quittez le panneau d'administration si vous y êtes encore) et allez dans `Catalog`.

À partir de là, vous pouvez voir la liste des sources de données connectées et les explorer en mode drill-down.

<img height="250" alt="Screenshot 2022-09-28 at 10 50 02" src="https://user-images.githubusercontent.com/690667/192734494-88edad37-669e-467f-9e75-737031286f3f.png">
<img height="250" alt="Screenshot 2022-09-28 at 10 50 16" src="https://user-images.githubusercontent.com/690667/192734511-a37287fc-8a3f-47a3-93bb-c8fb94d24d6c.png">

### Rechercher des données

Pour utiliser le moteur de recherche OpenHEXA, cliquez simplement sur recherche dans le menu principal ou appuyez sur `CMD-K`, ce qui ouvrira la modale de *recherche rapide*. À partir de là, vous pouvez soit :

- Saisir un terme de recherche et parcourir les résultats dans la modale de recherche
- Passer à la recherche avancée

La fonctionnalité de recherche avancée vous permettra de filtrer vos résultats de recherche par type de contenu et/ou par source de données.

<img height="250" alt="Screenshot 2022-09-28 at 10 52 50" src="https://user-images.githubusercontent.com/690667/192736910-edaf0d1b-5e8c-426f-b608-f8559c7d7b28.png">
<img height="250" alt="Screenshot 2022-09-28 at 10 59 53" src="https://user-images.githubusercontent.com/690667/192736931-d236d98c-4199-4213-9c82-574191465358.png">

## Utiliser les notebooks

L'environnement notebooks est un environnement [Jupyter](https://jupyter.org/) personnalisé.

Pour la plupart des fonctionnalités, vous pouvez vous référer à la [documentation officielle JupyterLab](https://jupyterlab.readthedocs.io/en/stable/).

OpenHEXA apporte quelques ajouts utiles aux fonctionnalités standard de Jupyter :

- Montage des buckets S3 / GCS dans le système de fichiers de votre serveur Jupyter pour un accès plus facile aux données
- Provisionnement de variables d'environnement pour les identifiants de vos sources de données
- Préinstallation d'une série de bibliothèques Python et R intéressantes

De plus, les pages de sources de données dans le catalogue de données fournissent généralement des exemples de code illustrant comment vous pouvez utiliser la source de données dans un notebook.

<img width="1326" alt="Screenshot 2022-09-28 at 12 00 24" src="https://user-images.githubusercontent.com/690667/192750757-06d597b0-d87b-477b-8053-41699a9be25c.png">

## Utiliser les pipelines de données

🚧 *Cette section est encore en cours de développement*

OpenHEXA utilise [Apache Airflow](https://airflow.apache.org/) pour exécuter les pipelines de données en arrière-plan.

Avant de pouvoir utiliser un pipeline de données, vous devez :

- Provisionner une instance Airflow et y connecter un dépôt Git pour les DAGs (voir les [instructions d'installation](installation.md))
- Configurer un Template DAG et un ou plusieurs DAGs à l'aide du panneau d'administration dans la section `Airflow Connector`
- Configurer les sources de données auxquelles le pipeline peut accéder (dans `Airflow Connector > Dag authorized datasources`)

Une fois votre DAG correctement configuré, vous pouvez voir le pipeline correspondant dans l'interface principale OpenHEXA et l'exécuter avec la configuration souhaitée.

<img width="600" alt="Screenshot 2022-09-28 at 12 10 48" src="https://user-images.githubusercontent.com/690667/192753050-9a305bd3-6fe7-49d8-9ecb-d52ea8d0670f.png">

<img width="600" alt="Screenshot 2022-09-28 at 12 10 57" src="https://user-images.githubusercontent.com/690667/192753093-84f1b090-6860-42c8-ad21-28778436efda.png">
