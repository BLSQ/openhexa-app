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
    - **Admins** : Peuvent parcourir les tables, visualiser les données, accéder aux identifiants de la base de données, écrire dans la base de données et régénérer le mot de passe de la base de données

![Database Interface](../assets/images/database/database.png)

Vous pouvez utiliser la base de données de l'espace de travail dans les notebooks OpenHEXA et les pipelines de données OpenHEXA.

Vous pouvez également utiliser votre base de données d'espace de travail OpenHEXA comme source de données dans des outils de visualisation de données et de BI comme Tableau ou Power BI. Copiez simplement les paramètres de connexion de la page de base de données et collez-les dans votre outil.

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


