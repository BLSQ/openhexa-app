<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Base de données</h1>
</div>
</div>
Chaque espace de travail dispose d'une base de données relationnelle PostgreSQL dédiée. Vous pouvez utiliser cette base de données pour stocker des données structurées (relationnelles) pour votre espace de travail. Vous pouvez facilement y accéder depuis des solutions de visualisation externes telles que Tableau ou Power BI.

## Fonctionnalités

Tous les membres de l'espace de travail peuvent parcourir les tables de la base de données et prévisualiser les données de chaque table. Cependant, l'accès aux identifiants de la base de données et les permissions d'écriture dépendent de votre rôle :

!!! info "Permissions de la base de données par rôle"
    - **Viewers** : Peuvent parcourir les tables et visualiser les données, mais ne peuvent pas voir les identifiants de la base de données ni écrire dans la base de données
    - **Editors** : Peuvent parcourir les tables, visualiser les données, accéder aux identifiants de la base de données et écrire dans la base de données
    - **Admins** : Peuvent parcourir les tables, visualiser les données, accéder aux identifiants de la base de données, écrire dans la base de données et régénérer les mots de passe de la base de données

![Database Interface](../assets/images/database/database.png)

Vous pouvez utiliser la base de données de l'espace de travail dans les notebooks OpenHEXA et les pipelines de données OpenHEXA.

Vous pouvez également utiliser votre base de données d'espace de travail OpenHEXA comme source de données dans des outils de visualisation de données et de BI comme Tableau ou Power BI. Copiez simplement les paramètres de connexion de la page de base de données et collez-les dans votre outil.

## Identifiants de la base de données

Chaque espace de travail fournit deux jeux d'identifiants de base de données :

### Connexion en lecture seule

La connexion en lecture seule est recommandée pour les outils de visualisation comme Superset, Power BI, Tableau et autres applications de tableaux de bord. Cette connexion permet uniquement les requêtes `SELECT`, empêchant les modifications accidentelles des données lors de l'exploration.

Les identifiants en lecture seule incluent :

- **Hôte** : L'adresse du serveur de base de données
- **Port** : Le port de connexion
- **Nom de base de données** : Le nom de votre base de données d'espace de travail
- **Nom d'utilisateur** : Un utilisateur en lecture seule (se terminant par `_ro`)
- **Mot de passe** : Mot de passe généré automatiquement
- **URL de connexion** : Une chaîne de connexion PostgreSQL complète

### Connexion en lecture/écriture (accès complet)

La connexion avec accès complet est destinée aux notebooks et aux pipelines qui doivent créer, mettre à jour ou supprimer des données. Utilisez ces identifiants lorsque votre code doit écrire dans la base de données.

!!! warning "Utilisez les identifiants en lecture seule pour les tableaux de bord"
    Lors de la connexion d'outils de visualisation, utilisez toujours les identifiants en lecture seule. Cela empêche les modifications accidentelles des données et respecte le principe du moindre privilège.

### Régénérer les mots de passe

Les Admins de l'espace de travail peuvent régénérer les mots de passe de la base de données s'ils sont compromis :

1. Accédez aux **Paramètres** de votre espace de travail.
2. Dans la section **Base de données**, cliquez sur **Régénérer le mot de passe** pour les identifiants que vous souhaitez réinitialiser.

!!! warning "Impact de la régénération du mot de passe"
    La régénération d'un mot de passe invalidera immédiatement l'ancien mot de passe. Tous les outils ou pipelines utilisant les anciens identifiants devront être mis à jour.

## Se connecter à Apache Superset

Apache Superset est une plateforme populaire open-source de visualisation et d'exploration de données. Vous pouvez connecter votre base de données d'espace de travail OpenHEXA à Superset pour des analyses avancées et la création de tableaux de bord.


1. **Accéder aux paramètres de connexion de la base de données**
    - Accédez à la page de base de données de votre espace de travail dans OpenHEXA.
    - Copiez les paramètres de connexion (hôte, port, nom de base de données, nom d'utilisateur et mot de passe).

2. **Ajouter la base de données dans Superset**
    - Dans Superset, accédez à **Paramètres** > **Connexions de base de données**.
    - Cliquez sur **+ Base de données** pour ajouter une nouvelle connexion.
    - Sélectionnez **PostgreSQL** comme type de base de données.

3. **Configurer la connexion**
    - **Hôte** : L'hôte de vos paramètres de base de données OpenHEXA
    - **Port** : Le port de vos paramètres de base de données OpenHEXA
    - **Nom de base de données** : Le nom de base de données de votre espace de travail
    - **Nom d'utilisateur** : Le nom d'utilisateur fourni
    - **Mot de passe** : Le mot de passe fourni
    - **Nom d'affichage** : Un nom descriptif pour votre connexion (par exemple, "Base de données d'espace de travail OpenHEXA")

4. **Tester et enregistrer**
    - Cliquez sur **Tester la connexion** pour vérifier la configuration.
    - Si réussi, cliquez sur **Connecter** pour enregistrer la connexion de base de données.
