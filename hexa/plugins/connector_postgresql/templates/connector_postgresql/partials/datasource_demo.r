library(DBI)

con <- dbConnect(
    RPostgres::Postgres(),
    dbname = Sys.getenv("{{ datasource.env_name }}_DATABASE"),
    host = Sys.getenv("{{ datasource.env_name }}_HOSTNAME"),
    port = Sys.getenv("{{ datasource.env_name }}_PORT"),
    user = Sys.getenv("{{ datasource.env_name }}_USERNAME"),
    password = Sys.getenv("{{ datasource.env_name }}_PASSWORD")
)

dbWriteTable(con, "some_table_name", Data_fin, overwrite=TRUE)
