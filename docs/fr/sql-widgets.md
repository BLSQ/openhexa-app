<div class="hero-section">
  <h1><i class="fas fa-chart-simple" style="margin-right: 0.5rem;"></i>Widgets SQL</h1>
</div>

Dans Data Studio, une requête affiche un graphique ou une carte au lieu d'un tableau lorsqu'elle renvoie des colonnes portant certains noms : `bar_label` et `bar_quantity` produisent un graphique à barres, tandis que `map_latitude` et `map_longitude` produisent une carte.

Une requête enregistrée devient ainsi un petit tableau de bord. Le widget apparaît dans un premier onglet et le résultat tabulaire habituel reste disponible dans un second : le graphique ou la carte ne masque donc aucune donnée.

## Conventions

| Graphique | Colonnes à renvoyer | Utilisation |
|-------|-------------------|------------|
| Barres | `bar_label`, `bar_quantity` | Comparer une mesure entre plusieurs catégories (districts, établissements, groupes d'âge) |
| Courbe | `line_x`, `line_y` | Montrer une tendance selon un axe ordonné (mois, semaines, périodes épidémiologiques) |
| Circulaire | `pie_label`, `pie_quantity` | Montrer la répartition d'un tout, lorsqu'il y a peu de catégories |
| Carte | `map_latitude`, `map_longitude` | Afficher des lieux dont les coordonnées sont connues (établissements, ménages, points d'enquête) |
| Carte | `map_geometry` | Afficher des zones plutôt que des points (districts, zones de desserte, régions) |

`*_label` et `*_x` correspondent à l'axe textuel ; `*_quantity` et `*_y` doivent contenir des nombres. `map_latitude` et `map_longitude` doivent contenir des nombres exprimés en degrés, et `map_geometry` doit contenir du GeoJSON.

## Règles de sélection du graphique

La requête doit renvoyer les colonnes requises par un widget. Les colonnes supplémentaires sont autorisées : un graphique les ignore et elles restent lisibles dans l'onglet du tableau. Une requête peut donc conserver un identifiant ou une colonne de filtre tout en produisant un graphique. Pour une carte, les colonnes supplémentaires apparaissent dans la fenêtre contextuelle de chaque entité ; nommez-les donc comme vous souhaitez les voir affichées. Si une requête renvoie simultanément les colonnes de plusieurs widgets, le premier correspondant est utilisé, dans l'ordre suivant : barres, courbe, circulaire, carte.

La colonne des valeurs doit contenir des nombres. Si elle contient du texte, le résultat revient au tableau plutôt que d'afficher un graphique trompeur. La même règle s'applique aux coordonnées : une valeur `map_latitude` hors de l'intervalle -90..90 ou une valeur `map_longitude` hors de l'intervalle -180..180 ne représente pas un lieu ; ces lignes ne sont pas affichées sur la carte.

**L'ordre des lignes détermine l'ordre du graphique.** Les graphiques ne réordonnent jamais les résultats : ils affichent les lignes dans l'ordre renvoyé par la requête. Ajoutez toujours un `ORDER BY` explicite — par valeur pour un graphique à barres, par date pour une courbe.

Agrégerez les données avant de créer un graphique. Un graphique contenant dix mille lignes brutes est illisible : utilisez `GROUP BY` pour regrouper les catégories et laissez la base de données effectuer le comptage. Un graphique à barres affiche au maximum 30 barres et un graphique circulaire regroupe toutes les parts après la sixième dans une seule part « Autres ». Utilisez donc `LIMIT` pour ne conserver que les catégories pertinentes.

## Cartographie

`map_latitude`/`map_longitude` est la forme la plus simple et à privilégier lorsque la table contient déjà des coordonnées numériques :

```sql
SELECT name, map_latitude, map_longitude FROM facilities;
```

Pour les zones, convertissez la géométrie en GeoJSON — une colonne de géométrie PostGIS renvoie du WKB binaire, qui ne peut pas être dessiné :

```sql
SELECT district AS name, ST_AsGeoJSON(geom) AS map_geometry
FROM districts;
```

Oublier `ST_AsGeoJSON` est une erreur fréquente ; Data Studio l'indique dans l'onglet de la carte au lieu de revenir silencieusement au tableau.

Les lignes sans emplacement exploitable sont exclues de la carte, qui affiche au maximum 2 000 entités. L'onglet du tableau contient toujours l'intégralité du résultat.

## Exemples

Nombre de cas par district, du plus élevé au plus faible :

```sql
SELECT district AS bar_label, COUNT(*) AS bar_quantity
FROM cases
GROUP BY district
ORDER BY bar_quantity DESC
LIMIT 15;
```

Tendance mensuelle dans une région :

```sql
SELECT TO_CHAR(reported_on, 'YYYY-MM') AS line_x, COUNT(*) AS line_y
FROM cases
WHERE region = 'Northern'
GROUP BY line_x
ORDER BY line_x;
```

Part des cas confirmés par type de test :

```sql
SELECT test_type AS pie_label, COUNT(*) AS pie_quantity
FROM cases
WHERE result = 'confirmed'
GROUP BY test_type
ORDER BY pie_quantity DESC;
```

Établissements d'une région, avec les colonnes affichées dans chaque fenêtre contextuelle :

```sql
SELECT name, type, beds, map_latitude, map_longitude
FROM facilities
WHERE region = 'Northern';
```

## Quand ne pas utiliser de widget

Utilisez une requête simple lorsque l'utilisateur veut consulter les enregistrements eux-mêmes, demande une liste précise de lignes ou que le résultat comporte plus de deux colonnes pertinentes. Un graphique répond à « comment ces valeurs se comparent-elles ? » ou « comment ont-elles évolué ? », et non à « affiche-moi les données ». Une carte répond à « où ? » : elle n'est utile que lorsque l'emplacement est au cœur de la question.

Les graphiques circulaires sont les plus faciles à mal utiliser : au-delà d'environ six catégories, ou lorsque les valeurs sont proches, un graphique à barres est plus lisible. Les valeurs doivent également être positives, puisqu'une part représente une fraction d'un tout ; les lignes dont les valeurs sont nulles ou négatives sont exclues du graphique circulaire.
