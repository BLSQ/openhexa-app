<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Fichiers</h1>
</div>
</div>
Chaque espace de travail comprend un système de fichiers partagé qui sert de fondation à l'architecture data lakehouse d'OpenHEXA. Ce système de fichiers fournit :

- Un emplacement centralisé pour stocker les fichiers de données brutes avant le traitement
- Un stockage intermédiaire pour les transformations de données et les pipelines
- Support pour les données structurées et non structurées
- Intégration avec les outils de traitement de données comme les notebooks et les pipelines

![File Management Interface](../assets/images/files/file_browser.png)

L'interface du navigateur de fichiers fournit plusieurs fonctionnalités clés :

- Rechercher des fichiers et des dossiers par nom
- Basculer la visibilité des fichiers cachés (commençant par ".")
- Créer des dossiers pour organiser votre espace de travail (Editors et Admins uniquement)
- Télécharger tout type de fichier dans votre espace de travail (Editors et Admins uniquement)

Les fichiers sont affichés dans un tableau montrant :

- Noms de fichiers/dossiers avec icônes de type
- Tailles de fichiers en format lisible  
- Dates de dernière modification avec capacité de tri

Vous pouvez effectuer des opérations courantes sur les fichiers :

- Télécharger des fichiers sur votre machine locale (tous les membres de l'espace de travail)
- Supprimer des fichiers et des dossiers lorsqu'ils ne sont plus nécessaires (Editors et Admins uniquement)

!!! info "Permissions des fichiers par rôle"
    - **Viewers** : Peuvent parcourir, rechercher et télécharger des fichiers
    - **Editors et Admins** : Peuvent parcourir, rechercher, télécharger, téléverser, créer des dossiers et supprimer des fichiers

## Intégration avec les outils OpenHEXA

Le système de fichiers de l'espace de travail s'intègre parfaitement avec les autres composants d'OpenHEXA :

- **Notebooks** : Accédez directement aux fichiers depuis les notebooks Jupyter en utilisant le système de fichiers de l'espace de travail. Voir [Notebooks](notebooks.md).
- **Pipelines de données** : Lisez et écrivez des fichiers dans vos flux de travail de traitement de données. Voir [OpenHEXA SDK](https://github.com/BLSQ/openhexa/wiki/Using-the-OpenHEXA-SDK).

