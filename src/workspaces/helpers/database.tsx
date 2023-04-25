type lang = "R" | "PYTHON";

export const getReadTableSnippet = (tableName: string) => {
  return `import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.environ["WORKSPACE_DATABASE_URL"])

pd.read_sql("SELECT * FROM ${tableName}", con=engine)`;
};

export const getUsageSnippet = (tableName: string, lang: lang) => {
  let text = "";
  switch (lang) {
    case "PYTHON":
      text = `import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.environ["WORKSPACE_DATABASE_URL"])

# Create sample dataframe
df = pd.DataFrame({"name": ["Jane", "John", "Tyler"], "age": [19, 17, 22]})

# Write data
df.to_sql("${tableName}", con=engine, if_exists="replace")`;
      break;
    case "R":
      text = `library(DBI)
  
con <- dbConnect(
    RPostgres::Postgres(),
    dbname = Sys.getenv("WORKSPACE_DATABASE_DB_NAME"),
    host = Sys.getenv("WORKSPACE_DATABASE_HOST"),
    port = Sys.getenv("WORKSPACE_DATABASE_PORT"),
    user = Sys.getenv("WORKSPACE_DATABASE_USERNAME"),
    password = Sys.getenv("WORKSPACE_DATABASE_PASSWORD")
)

dbWriteTable(con, "${tableName}", Data_fin, overwrite=TRUE)`;
      break;
  }
  return text;
};
