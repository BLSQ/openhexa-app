import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import { FormInstance } from "core/hooks/useForm";
import { Connection, ConnectionType } from "graphql/types";
import {
  DeleteConnectionMutation,
  DeleteConnectionMutationVariables,
} from "./utils.generated";

export type FieldForm = {
  secret?: boolean;
  code: string;
  value?: string | null;
} & {
  [key: string]: any;
};

export type ConnectionForm = {
  name: string;
  description?: string;
  type: ConnectionType | null;
  [key: string]: any;
};

export type ConnectionDefinition = {
  label: string;
  color: string;
  iconSrc?: string;
  fields: FieldForm[];
  Form: React.FC<{ form: FormInstance<ConnectionForm> }>;
};

export const updateFormField = (
  form: FormInstance<ConnectionForm>,
  index: number,
  values: any,
) => {
  const newFields = [...(form.formData.fields ?? [])];
  newFields.splice(index, 1, { ...newFields[index], ...values });
  form.setFieldValue("fields", newFields);
};

export const slugify = (...keys: string[]) =>
  keys.join("_").replaceAll("-", "_").toUpperCase();

export function convertFieldsToInput(
  connectionType: ConnectionDefinition,
  fields: { [key: string]: any },
) {
  return connectionType.fields.map((f: any) => ({
    code: f.code,
    secret: Boolean(f.secret),
    value: fields[f.code],
  }));
}

export function getUsageSnippets(
  connection: Pick<Connection, "slug" | "type"> & {
    fields: { code: string }[];
  },
) {
  switch (connection.type) {
    case ConnectionType.Dhis2:
      return [
        {
          lang: "python",
          code: `# Importing os module 
import os

DHIS2_URL = os.getenv("${slugify(connection.slug, "url")}")
DHIS2_USERNAME = os.getenv("${slugify(connection.slug, "username")}")
DHIS2_PASSWORD = os.getenv("${slugify(connection.slug, "password")}")
`,
        },
      ];
    case ConnectionType.Postgresql:
      return [
        {
          lang: "python",
          code: `# using sqlalchemy
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.environ["${slugify(connection.slug, "url")}"])

# Create sample dataframe
df = pd.DataFrame({"name": ["Jane", "John", "Tyler"], "age": [19, 17, 22]})

# Write data
df.to_sql("database_tutorial", con=engine, if_exists="replace")

# Read data
pd.read_sql("SELECT * FROM database_tutorial", con=engine)

#using psycopg2

#Importing os module 
import os

# import postgresql library
import psycopg2

# Create the connection to the database
conn = psycopg2.connect(
  database=os.getenv("${slugify(connection.slug, "db_name")}"),
  host=os.getenv("${slugify(connection.slug, "host")}"),
  user=os.getenv("${slugify(connection.slug, "username")}"),
  password=os.getenv("${slugify(connection.slug, "password")}"),
  port=os.getenv("${slugify(connection.slug, "port")}")
)

# Create a DB session
cursor = conn.cursor()
`,
        },
        {
          lang: "r",
          code: `library(DBI)

con <- dbConnect(
    RPostgres::Postgres(),
    dbname = Sys.getenv("${slugify(connection.slug, "db_name")}"),
    host = Sys.getenv("${slugify(connection.slug, "host")}"),
    port = Sys.getenv("${slugify(connection.slug, "port")}"),
    user = Sys.getenv("${slugify(connection.slug, "username")}"),
    password = Sys.getenv("${slugify(connection.slug, "password")}")
)

dbWriteTable(con, "some_table_name", Data_fin, overwrite=TRUE)`,
        },
      ];
    case ConnectionType.S3:
      return [
        {
          lang: "python",
          code: `# importing os module 
import os

# Reading and writing to S3 using Pandas
import pandas as pd
import boto3

AWS_S3_BUCKET = os.getenv("${slugify(connection.slug, "bucket_name")}")
AWS_ACCESS_KEY_ID = os.getenv("${slugify(connection.slug, "access_key_id")}")
AWS_SECRET_ACCESS_KEY = os.getenv("${slugify(
            connection.slug,
            "access_key_secret",
          )}")
AWS_SESSION_TOKEN = None
  
s3_client = boto3.client(
  "s3",
  aws_access_key_id=AWS_ACCESS_KEY_ID,
  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
  aws_session_token=AWS_SESSION_TOKEN,
)
books_df = pd.DataFrame(
  data={"Title": ["Book I", "Book II", "Book III"], "Price": [56.6, 59.87, 74.54]},
  columns=["Title", "Price"],
)


with io.StringIO() as csv_buffer:
  books_df.to_csv(csv_buffer, index=False)

  response = s3_client.put_object(
      Bucket=AWS_S3_BUCKET, Key="files/books.csv", Body=csv_buffer.getvalue()
  )

  status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

  if status == 200:
      print(f"Successful S3 put_object response. Status - {status}")
  else:
      print(f"Unsuccessful S3 put_object response. Status - {status}")
`,
        },
      ];
    case ConnectionType.Custom:
      return [
        {
          lang: "python",
          code: `# Importing os module 
import os

# Get connection fields from environment variables
${connection.fields
  .map(
    (f) => `${slugify(connection.slug, f.code)} = os.getenv("${slugify(
      connection.slug,
      f.code,
    )}")
`,
  )
  .join("")}
`,
        },
      ];
    default:
      return [];
  }
}

export async function deleteConnection(connectionId: string) {
  const client = getApolloClient();
  const { data } = await client.mutate<
    DeleteConnectionMutation,
    DeleteConnectionMutationVariables
  >({
    mutation: gql`
      mutation DeleteConnection($input: DeleteConnectionInput!) {
        deleteConnection(input: $input) {
          success
          errors
        }
      }
    `,
    variables: { input: { id: connectionId } },
    update(cache) {
      const normalizedId = cache.identify({
        id: connectionId,
        __typename: "Connection",
      });

      cache.evict({ id: normalizedId });
      cache.gc();
    },
  });

  if (!data?.deleteConnection.success) {
    throw new Error("Impossible to delete connection");
  }
  return true;
}
