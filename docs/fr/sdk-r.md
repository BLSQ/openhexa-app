<div class="hero-section">
  <h1><i class="fab fa-r-project" style="margin-right: 0.5rem;"></i>Utiliser le SDK R OpenHEXA</h1>
</div>
</div>

Le package R `openhexa` est le client R d'OpenHEXA : charger des fichiers, des jeux de données et des requêtes enregistrées dans des data frames, utiliser la base de données de l'espace de travail, publier des web apps et lancer des pipelines.

Il fonctionne depuis un notebook OpenHEXA, depuis RStudio, ou depuis un script exécuté n'importe où.

Le code source, le journal des modifications et le suivi des problèmes se trouvent dans le dépôt [`openhexa-sdk-r`](https://github.com/BLSQ/openhexa-sdk-r). Chaque fonction est documentée dans R : exécutez `?get_dataset_file`, ou `help(package = "openhexa")` pour la liste complète.

Vous cherchez Python ? Consultez [Utiliser le SDK OpenHEXA](sdk.md).

## Installation

Le package est préinstallé dans les notebooks OpenHEXA. Ailleurs, installez la dernière version depuis GitHub :

```r
# install.packages("remotes")
remotes::install_github("BLSQ/openhexa-sdk-r")
```

Les versions sont étiquetées sur GitHub (`v0.1.0`, `v0.2.0`, ...). Pour installer une version précise :

```r
remotes::install_github("BLSQ/openhexa-sdk-r@v0.2.0")
```

Pour figer la version d'un projet, utilisez [renv](https://rstudio.github.io/renv/) : il enregistre la version dans un fichier de verrouillage qui restaure le même environnement sur un autre ordinateur, ou dans un espace de travail OpenHEXA.

```r
renv::install("BLSQ/openhexa-sdk-r@v0.2.0")
renv::snapshot()
```

Les versions suivent le [versionnage sémantique](https://semver.org/lang/fr/). Avant la 1.0.0, les changements incompatibles augmentent la version mineure (de 0.1.x à 0.2.0) : figer la version mineure vous en protège.

## S'authentifier et explorer

Dans les notebooks OpenHEXA et les pipelines de notebooks R, le package est déjà chargé et configuré : vous pouvez appeler ses fonctions directement, sans `library(openhexa)` ni `login()`.

Ailleurs, copiez votre jeton d'API depuis les paramètres de votre compte (voir [Authentification API](api-authentication.md)) et connectez-vous :

```r
library(openhexa)
login(server_url = "https://api.openhexa.org") # demande votre jeton d'API

list_workspaces()
set_workspace("my-workspace")

list_datasets()
list_files("examples/")
list_saved_queries()
list_webapps()
list_pipelines()
list_connections()

# Chaque fonction accepte aussi un espace de travail, pour en utiliser un autre sans changer
list_datasets(workspace = "other-workspace")
```

Pour éviter l'étape de connexion, définissez `HEXA_SERVER_URL`, `HEXA_TOKEN` et `HEXA_WORKSPACE` dans votre `~/.Renviron` (`usethis::edit_r_environ()`), puis redémarrez R. Dans un script, lisez le jeton depuis une variable d'environnement pour qu'il n'apparaisse pas dans le code :

```r
login(
  server_url = "https://api.openhexa.org",
  token = Sys.getenv("OPENHEXA_TOKEN"),
  workspace = "my-workspace"
)
```

!!! warning "Attention"
    Utilisez l'URL de l'**API** de votre instance OpenHEXA (par ex. `https://api.openhexa.org`), et non l'URL de l'interface web.

## Lire et écrire des fichiers

Les fichiers de l'espace de travail (voir [Fichiers](files.md)) peuvent être lus directement dans un data frame. Les formats CSV, TSV, Parquet, Excel, JSON et RDS sont pris en charge.

```r
cases <- get_file("examples/cases.csv")

# Télécharger un fichier sans le lire
download_file("examples/cases.csv", dest = "cases_copy.csv")

# Envoyer un fichier local dans l'espace de travail
write.csv(cases, "cases.csv", row.names = FALSE)
upload_file("cases.csv", "examples/cases.csv")
```

Dans les notebooks OpenHEXA, le système de fichiers de l'espace de travail est aussi monté sous `/home/hexa/workspace` : vous pouvez donc continuer à utiliser `read.csv()` et les fonctions similaires avec ce chemin.

## Travailler avec les jeux de données

```r
# Un jeu de données, ses versions et ses fichiers
get_dataset("example-malaria-cases")
list_dataset_versions("example-malaria-cases")
list_dataset_files("example-malaria-cases")

# Un fichier du jeu de données, de la dernière version ou d'une version donnée
get_dataset_file("example-malaria-cases", "cases.csv", version = "2024")

# Toutes les tables d'une version, empilées, avec une colonne `file`
get_dataset_data("example-malaria-cases")

# Créer un jeu de données, une version, et y ajouter un fichier
dataset <- create_dataset("Example malaria cases")$slug
create_dataset_version(dataset, "2024")
add_dataset_file(dataset, "cases.csv")
```

Consultez [Jeux de données](datasets.md) pour plus d'informations sur les jeux de données dans OpenHEXA.

## Utiliser la base de données de l'espace de travail

`connect_database()` renvoie une connexion [DBI](https://dbi.r-dbi.org/) à la [base de données](database.md) de l'espace de travail. Elle nécessite les packages `DBI` et `RPostgres`.

```r
con <- connect_database()
DBI::dbWriteTable(con, "example_cases", cases, overwrite = TRUE)
DBI::dbGetQuery(con, "SELECT district, SUM(cases) AS cases FROM example_cases GROUP BY district")
DBI::dbDisconnect(con)
```

Les requêtes enregistrées dans le Data Studio peuvent être exécutées directement, et leur résultat est renvoyé sous forme de data frame :

```r
queries <- list_saved_queries()
run_saved_query(queries$slug[1], max_rows = 10000)
```

## Publier des web apps

`publish_webapp()` accepte une chaîne HTML, un fichier HTML, un dossier contenant un `index.html`, ou un htmlwidget (plotly, leaflet, DT, ...), et renvoie la web app avec son `url` :

```r
publish_webapp("Hello", "<h1>Hello from R</h1>")

# Un graphique interactif (install.packages("plotly"))
chart <- plotly::plot_ly(cases, x = ~month, y = ~cases, color = ~district, type = "scatter", mode = "lines")
publish_webapp("Malaria cases", chart)$url

# Un rapport Quarto rendu dans un seul fichier HTML
quarto::quarto_render("report.qmd")
publish_webapp("Malaria report", "report.html")$url
```

Publier à nouveau sous le même nom remplace le contenu de la web app : l'URL reste donc la même. Consultez [Webapps statiques](static-webapps.md) pour plus d'informations.

## Créer des notebooks

```r
create_notebook("examples/malaria.ipynb", c(
  markdown = "# Malaria cases",
  "cases <- get_dataset_file('example-malaria-cases', 'cases.csv')",
  "summary(cases)"
))
```

## Pipelines et connexions

Les pipelines sont déployés sur OpenHEXA, et les [connexions](connections.md) sont configurées dans les paramètres de l'espace de travail. Depuis R, vous lancez les pipelines et lisez les connexions :

```r
code <- list_pipelines()$code[1]
get_pipeline(code) # ses paramètres, à passer dans config

run <- run_pipeline(code, config = list(start_date = "2024-01-01"), wait = TRUE)
run$status
run$messages
list_pipeline_runs(code)

connection <- list_connections()$identifier[1]
get_connection(connection) # les valeurs secrètes sont masquées à l'affichage
```

Dans un pipeline, comme un pipeline de notebook R, envoyez des messages à la page d'exécution avec `current_run` (l'équivalent de `current_run.log_info()` en Python). En dehors d'un pipeline, ils sont affichés dans la console.

```r
current_run$log_info("Read ", nrow(cases), " rows")
```

## Erreurs et serveurs multiples

Les erreurs ont des classes (`openhexa_not_found_error`, `openhexa_permission_error`, ...) et peuvent donc être gérées avec `tryCatch()` :

```r
dataset <- tryCatch(
  get_dataset("example-malaria-cases")$slug,
  openhexa_not_found_error = function(e) create_dataset("Example malaria cases")$slug
)
```

Pour utiliser plusieurs serveurs ou jetons dans la même session, créez des clients et passez-les via `client` :

```r
demo <- openhexa_client("https://api.demo.openhexa.org", Sys.getenv("OPENHEXA_DEMO_TOKEN"))
list_workspaces(client = demo)
```

## Utilisation avancée : requêtes GraphQL

Pour tout le reste, `graphql_query()` exécute n'importe quelle requête sur l'API GraphQL d'OpenHEXA.

!!! warning "Attention"
    L'API GraphQL est interne à OpenHEXA et **change sans préavis** : une requête qui fonctionne aujourd'hui peut ne plus fonctionner après la prochaine version d'OpenHEXA, et le versionnage sémantique ne la couvre pas. Utilisez les fonctions dédiées dès qu'elles existent, et demandez à l'équipe OpenHEXA d'ajouter une fonction si vous avez besoin de quelque chose qu'elles ne font pas.
