<div class="hero-section">
  <h1><i class="fab fa-r-project" style="margin-right: 0.5rem;"></i>Using the OpenHEXA R SDK</h1>
</div>
</div>

The `openhexa` R package is the R client for OpenHEXA: load files, datasets and saved queries into data frames, use the workspace database, publish web apps and run pipelines.

It works from an OpenHEXA notebook, from RStudio, or from a script running anywhere.

The source code, changelog and issue tracker live in the [`openhexa-sdk-r`](https://github.com/BLSQ/openhexa-sdk-r) repository. Every function is documented in R: run `?get_dataset_file`, or `help(package = "openhexa")` for the full list.

Looking for Python? See [Using the OpenHEXA SDK](sdk.md).

## Installation

The package is preinstalled in OpenHEXA notebooks. Elsewhere, install the latest release from GitHub:

```r
# install.packages("remotes")
remotes::install_github("BLSQ/openhexa-sdk-r")
```

Releases are tagged on GitHub (`v0.1.0`, `v0.2.0`, ...). To install a specific version:

```r
remotes::install_github("BLSQ/openhexa-sdk-r@v0.2.0")
```

To pin the version for a project, use [renv](https://rstudio.github.io/renv/): it records the version in a lockfile that restores the same environment on another computer, or in an OpenHEXA workspace.

```r
renv::install("BLSQ/openhexa-sdk-r@v0.2.0")
renv::snapshot()
```

Versions follow [semantic versioning](https://semver.org). Before 1.0.0, breaking changes increase the minor version (0.1.x to 0.2.0), so pinning the minor version protects you from them.

## Authenticate and explore

In OpenHEXA notebooks and R notebook pipelines, the package is already loaded and configured: you can call its functions directly, without `library(openhexa)` or `login()`.

Elsewhere, copy your API token from your account settings (see [API Authentication](api-authentication.md)) and log in:

```r
library(openhexa)
login(server_url = "https://api.openhexa.org") # prompts for your API token

list_workspaces()
set_workspace("my-workspace")

list_datasets()
list_files("examples/")
list_saved_queries()
list_webapps()
list_pipelines()
list_connections()

# Every function also takes a workspace, to work with another one without switching
list_datasets(workspace = "other-workspace")
```

To skip the login step, set `HEXA_SERVER_URL`, `HEXA_TOKEN` and `HEXA_WORKSPACE` in your `~/.Renviron` (`usethis::edit_r_environ()`), then restart R. In a script, read the token from an environment variable to keep it out of the code:

```r
login(
  server_url = "https://api.openhexa.org",
  token = Sys.getenv("OPENHEXA_TOKEN"),
  workspace = "my-workspace"
)
```

!!! warning
    Use the **API** URL of your OpenHEXA instance (e.g. `https://api.openhexa.org`), not the URL of the web interface.

## Reading and writing files

Workspace files (see [Files](files.md)) can be read directly into a data frame. CSV, TSV, Parquet, Excel, JSON and RDS files are supported.

```r
cases <- get_file("examples/cases.csv")

# Download a file without reading it
download_file("examples/cases.csv", dest = "cases_copy.csv")

# Upload a local file to the workspace
write.csv(cases, "cases.csv", row.names = FALSE)
upload_file("cases.csv", "examples/cases.csv")
```

In OpenHEXA notebooks, the workspace filesystem is also mounted under `/home/hexa/workspace`, so you can keep using `read.csv()` and friends with that path.

## Working with datasets

```r
# A dataset, its versions and files
get_dataset("example-malaria-cases")
list_dataset_versions("example-malaria-cases")
list_dataset_files("example-malaria-cases")

# A dataset file, from the latest version or a given one
get_dataset_file("example-malaria-cases", "cases.csv", version = "2024")

# All the tables of a version, stacked, with a `file` column
get_dataset_data("example-malaria-cases")

# Create a dataset, a version, and add a file to it
dataset <- create_dataset("Example malaria cases")$slug
create_dataset_version(dataset, "2024")
add_dataset_file(dataset, "cases.csv")
```

See [Datasets](datasets.md) for more information about datasets in OpenHEXA.

## Using the workspace database

`connect_database()` returns a [DBI](https://dbi.r-dbi.org/) connection to the workspace [database](database.md). It requires the `DBI` and `RPostgres` packages.

```r
con <- connect_database()
DBI::dbWriteTable(con, "example_cases", cases, overwrite = TRUE)
DBI::dbGetQuery(con, "SELECT district, SUM(cases) AS cases FROM example_cases GROUP BY district")
DBI::dbDisconnect(con)
```

Saved queries written in the Data Studio can be run directly, and their result is returned as a data frame:

```r
queries <- list_saved_queries()
run_saved_query(queries$slug[1], max_rows = 10000)
```

## Publishing web apps

`publish_webapp()` takes a string of HTML, an HTML file, a folder with an `index.html`, or an htmlwidget (plotly, leaflet, DT, ...), and returns the web app with its `url`:

```r
publish_webapp("Hello", "<h1>Hello from R</h1>")

# An interactive chart (install.packages("plotly"))
chart <- plotly::plot_ly(cases, x = ~month, y = ~cases, color = ~district, type = "scatter", mode = "lines")
publish_webapp("Malaria cases", chart)$url

# A Quarto report rendered to a single HTML file
quarto::quarto_render("report.qmd")
publish_webapp("Malaria report", "report.html")$url
```

Publishing again under the same name replaces the content of the web app, so the URL stays the same. See [Static Webapps](static-webapps.md) for more information.

## Creating notebooks

```r
create_notebook("examples/malaria.ipynb", c(
  markdown = "# Malaria cases",
  "cases <- get_dataset_file('example-malaria-cases', 'cases.csv')",
  "summary(cases)"
))
```

## Pipelines and connections

Pipelines are deployed to OpenHEXA, and [connections](connections.md) are set up in the workspace settings. From R, you run the pipelines and read the connections:

```r
code <- list_pipelines()$code[1]
get_pipeline(code) # its parameters, to pass in config

run <- run_pipeline(code, config = list(start_date = "2024-01-01"), wait = TRUE)
run$status
run$messages
list_pipeline_runs(code)

connection <- list_connections()$identifier[1]
get_connection(connection) # secret values are hidden when printed
```

Inside a pipeline, such as an R notebook pipeline, send messages to the run page with `current_run` (the equivalent of `current_run.log_info()` in Python). Outside a pipeline, they are printed in the console.

```r
current_run$log_info("Read ", nrow(cases), " rows")
```

## Errors and multiple servers

Errors have classes (`openhexa_not_found_error`, `openhexa_permission_error`, ...), so they can be handled with `tryCatch()`:

```r
dataset <- tryCatch(
  get_dataset("example-malaria-cases")$slug,
  openhexa_not_found_error = function(e) create_dataset("Example malaria cases")$slug
)
```

To work with several servers or tokens in the same session, build clients and pass them as `client`:

```r
demo <- openhexa_client("https://api.demo.openhexa.org", Sys.getenv("OPENHEXA_DEMO_TOKEN"))
list_workspaces(client = demo)
```

## Advanced usage: GraphQL queries

For anything else, `graphql_query()` runs any query against the OpenHEXA GraphQL API.

!!! warning
    The GraphQL API is internal to OpenHEXA and **changes without notice**: a query that works today can break after the next OpenHEXA release, and semantic versioning doesn't cover it. Use the dedicated functions whenever they exist, and ask the OpenHEXA team to add a function if you need something they don't do.
