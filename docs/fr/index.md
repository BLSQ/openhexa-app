<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Documentation OpenHEXA</h1>
  <p>Guide complet de la plateforme d'intégration de données open-source pour les projets de santé publique</p>
  <div class="hero-buttons">
    <a href="https://openhexa.com" class="hero-btn primary"><i class="fas fa-book" style="margin-right: 0.5rem;"></i>Site Web</a>
    <a href="https://github.com/BLSQ/openhexa" class="hero-btn"><i class="fab fa-github" style="margin-right: 0.5rem;"></i>GitHub</a>
  </div>
</div>

## Bienvenue sur OpenHEXA

OpenHEXA est une plateforme d'intégration de données open-source développée par [Bluesquare](https://bluesquarehub.com) pour faciliter l'intégration et l'analyse de données, particulièrement dans le contexte de projets de santé publique.

![Workspace Switcher](../assets/images/openhexa.png){ width=70% align=center }


Cette documentation fournit des guides complets pour utiliser OpenHEXA efficacement, de la navigation de base au développement avancé de pipelines.

## Aperçu de la documentation

### 📚 Manuel d'utilisation

Ce manuel d'utilisation couvre tous les aspects de l'utilisation d'OpenHEXA :

<div class="quickstart-grid">
  <div class="quickstart-card">
    <div class="number">👤</div>
    <h3><a href="account.md">Gestion du compte</a></h3>
    <p>Gérez votre profil, vos paramètres de sécurité et vos préférences personnelles.</p>
  </div>
  
  <div class="quickstart-card">
    <div class="number">🧭</div>
    <h3><a href="navigation.md">Navigation</a></h3>
    <p>Apprenez à naviguer entre les organisations, les espaces de travail et à trouver rapidement des ressources.</p>
  </div>
  
  <div class="quickstart-card">
    <div class="number">🏢</div>
    <h3><a href="workspaces.md">Espaces de travail</a></h3>
    <p>Créez et gérez des environnements de projet collaboratifs pour votre équipe.</p>
  </div>
  
  <div class="quickstart-card">
    <div class="number">📁</div>
    <h3><a href="files.md">Gestion des fichiers</a></h3>
    <p>Téléchargez, organisez et partagez des fichiers via le système de fichiers partagé.</p>
  </div>
  
  <div class="quickstart-card">
    <div class="number">🗄️</div>
    <h3><a href="database.md">Base de données</a></h3>
    <p>Travaillez avec des bases de données PostgreSQL pour le stockage et l'analyse de données structurées.</p>
  </div>
  
  <div class="quickstart-card">
    <div class="number">📊</div>
    <h3><a href="datasets.md">Jeux de données</a></h3>
    <p>Gérez et versionnez vos jeux de données pour une analyse reproductible.</p>
  </div>
  
  <div class="quickstart-card">
    <div class="number">🔗</div>
    <h3><a href="connections.md">Connexions</a></h3>
    <p>Connectez-vous à des sources de données externes et à des API pour l'intégration de données.</p>
  </div>
  
  <div class="quickstart-card">
    <div class="number">⚡</div>
    <h3><a href="pipelines.md">Pipelines</a></h3>
    <p>Créez, exécutez et planifiez des flux de travail de données complexes et des processus ETL.</p>
  </div>
  
  <div class="quickstart-card">
    <div class="number">📓</div>
    <h3><a href="notebooks.md">Notebooks</a></h3>
    <p>Utilisez les notebooks Jupyter pour l'exploration et l'analyse interactives de données.</p>
  </div>
</div>

## Démarrer avec OpenHEXA

### 🚀 Pour les nouveaux utilisateurs

Si vous êtes nouveau sur OpenHEXA, suivez ce parcours d'apprentissage :

1. **[Gestion du compte](account.md)** - Configurez votre profil et vos paramètres de sécurité
2. **[Navigation](navigation.md)** - Apprenez à naviguer efficacement sur la plateforme
3. **[Espaces de travail](workspaces.md)** - Créez votre premier espace de travail et comprenez l'environnement
4. **[Gestion des fichiers](files.md)** - Téléchargez et organisez vos fichiers de données
5. **[Notebooks](notebooks.md)** - Commencez à explorer les données avec les notebooks Jupyter

### 🛠️ Pour les développeurs

Si vous prévoyez de développer des pipelines ou de travailler avec l'API :

- **[Écrire des pipelines OpenHEXA](writing-pipelines.md)** - Créez des flux de travail de données personnalisés
- **[Webapps statiques](static-webapps.md)** - Héberger des applications web statiques dans OpenHEXA
- **[Utiliser l'OpenHEXA CLI](cli.md)** - Interface en ligne de commande
- **[Utiliser l'OpenHEXA SDK](sdk.md)** - Kit de développement Python
- **[Utiliser l'OpenHEXA Toolbox - DHIS2](toolbox-dhis2.md)** - Acquérir et traiter des données depuis des instances DHIS2
- **[Utiliser l'OpenHEXA Toolbox - IASO](toolbox-iaso.md)** - Récupérer des données depuis IASO
- **[Client OpenHEXA](toolbox-hexa.md)** - Client GraphQL typé pour la plateforme OpenHEXA
- **[Utiliser les notebooks dans OpenHEXA](notebooks-advanced.md)** - Utilisation avancée des notebooks
- **[Authentification API](api-authentication.md)** - S'authentifier auprès de l'API OpenHEXA


### 👥 Pour les administrateurs

Si vous gérez des équipes et des organisations :

1. **[Administration](admin.md)** - Gérez les organisations, les espaces de travail et les utilisateurs
2. **[Espaces de travail](workspaces.md)** - Configurez les paramètres et les permissions des espaces de travail
3. **[Authentification unique (SSO)](sso.md)** - Configurez des fournisseurs d'identité OIDC externes

### 🔧 Installation et administration

- **[Instructions d'installation](installation.md)** - Configurez votre instance OpenHEXA
- **[Instructions d'installation locale](https://github.com/BLSQ/openhexa?tab=readme-ov-file#quick-start)** - Configurez votre instance OpenHEXA localement
- **[Architecture technique](architecture.md)** - Conception du système et composants


### 🔍 Besoin d'aide ?

- **Discussions GitHub** : [Q&R de la communauté](https://github.com/BLSQ/openhexa/discussions) - Posez des questions et partagez des connaissances
- **Issues GitHub** : [Signaler des bugs et demander des fonctionnalités](https://github.com/BLSQ/openhexa/issues)
- **Documentation** : Vous êtes ici ! 📚 - Guides complets et références

### 🔗 Ressources externes

- **Dépôt GitHub** : [BLSQ/openhexa](https://github.com/BLSQ/openhexa) - Code source et développement
- **Package PyPI** : [openhexa](https://pypi.org/project/openhexa/) - SDK et outils Python
- **Bluesquare** : [Site web de l'entreprise](https://bluesquarehub.com) - En savoir plus sur les développeurs



---

<div class="cta-section">
  <h2>Prêt à transformer vos données en insights ?</h2>
  <p>Rejoignez la communauté croissante d'organisations de santé publique utilisant OpenHEXA pour leurs besoins d'intégration de données.</p>
  <div class="hero-buttons">
    <a href="https://openhexa.com" class="hero-btn">Visitez www.openhexa.com</a>
  </div>
</div>


*OpenHEXA est développé avec ❤️ par [Bluesquare](https://bluesquarehub.com) pour la communauté mondiale de la santé publique.*

