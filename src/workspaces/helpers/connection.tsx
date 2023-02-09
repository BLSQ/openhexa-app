import { gql } from "@apollo/client";
import { PlusCircleIcon, XMarkIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Checkbox from "core/components/forms/Checkbox";
import Field from "core/components/forms/Field";
import Title from "core/components/Title";
import { getApolloClient } from "core/helpers/apollo";
import { FormInstance } from "core/hooks/useForm";
import { Connection, ConnectionType } from "graphql-types";
import { useCallback, useEffect, useMemo } from "react";
import { useTranslation } from "react-i18next";
import {
  DeleteConnectionMutation,
  DeleteConnectionMutationVariables,
} from "./connection.generated";

type FieldForm = { secret?: boolean; code: string; value?: string | null } & {
  [key: string]: any;
};

export type ConnectionForm = {
  name: string;
  description?: string;
  slug?: string;
  type: ConnectionType | null;
  fields: FieldForm[];
};

const updateFormField = (
  form: FormInstance<ConnectionForm>,
  index: number,
  values: any
) => {
  const newFields = [...(form.formData.fields ?? [])];
  newFields.splice(index, 1, { ...newFields[index], ...values });
  form.setFieldValue("fields", newFields);
};

export function getUsageSnippets(
  connection: Pick<Connection, "slug" | "type"> & {
    fields: { code: string }[];
  }
) {
  const slugify = (...keys: string[]) =>
    keys.join("_").replace("-", "_").toUpperCase();

  switch (connection.type) {
    case ConnectionType.Dhis2:
      return [
        {
          lang: "python",
          code: `# Importing os module 
import os

DHIS2_URL = os.getenv("${slugify(connection.slug, "api_url")}")
DHIS2_USERNAME = os.getenv("${slugify(connection.slug, "username")}")
DHIS2_PASSWORD = os.getenv("${slugify(connection.slug, "password")}")
`,
        },
      ];
    case ConnectionType.Postgresql:
      return [
        {
          lang: "python",
          code: `# Importing os module 
import os

# import postgresql library
import psycopg2

# Create the connection to the database
conn = psycopg2.connect(
  database=os.getenv("${slugify(connection.slug, "db_name")}"),
  host=os.getenv("${slugify(connection.slug, "host")}"),
  user=os.getenv("${slugify(connection.slug, "user")}"),
  password=os.getenv("${slugify(connection.slug, "password")}"),
  port=os.getenv("${slugify(connection.slug, "port")}")
)

# Create a DB session
cursor = conn.cursor()
`,
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
            "access_key_secret"
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
      f.code
    )}")
`
  )
  .join("")}
`,
        },
      ];
    default:
      return [];
  }
}

function updateFieldByCode(
  form: FormInstance<ConnectionForm>,
  field: FieldForm
) {
  const idx = form.formData.fields?.findIndex((f) => f.code === field.code);
  if (idx !== undefined && idx > -1) {
    updateFormField(form, idx, field);
  } else {
    form.setFieldValue("fields", [...(form.formData.fields ?? []), field]);
  }
}

const useConnectionFields = (
  form: FormInstance<ConnectionForm>,
  defaultFields: {
    code: string;
    name: string;
    secret?: boolean;
    value?: any;
  }[]
) => {
  const data = useMemo(() => {
    const result = defaultFields.map(
      (defaultField) =>
        form.formData.fields?.find((f) => f.code === defaultField.code) ??
        defaultField
    );
    return result.reduce((acc, current) => {
      acc[current.code] = current;
      return acc;
    }, {} as any);
    // We do not want this hook to be called if the reference of fieldTemplates changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.formData.fields]);

  const updateField = useCallback(
    (code: string, value: any) => {
      const field = data[code];
      updateFieldByCode(form, { ...field, value });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [data, form.formData.fields]
  );

  useEffect(() => {
    // Update the form with the fields
    form.setFieldValue("fields", defaultFields);

    // Only set fields on first mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return [data, { updateField }] as const;
};

function PostgreSQLForm(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  const [{ db_name, host, port, user, password }, { updateField }] =
    useConnectionFields(form, [
      { code: "db_name", name: "DB Name" },
      { code: "host", name: "Host" },
      { code: "port", name: "Port" },
      { code: "user", name: "User" },
      { code: "password", secret: true, name: "Password" },
    ]);

  return (
    <>
      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={db_name.value}
        name="db_name"
        label={t("Database name")}
        required
      />
      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={host.value}
        name="host"
        label={t("Host")}
        required
      />
      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={port.value}
        name="port"
        type="number"
        label={t("Port")}
        required
      />

      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={user.value}
        name="user"
        label={t("User")}
        required
      />

      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={password.value}
        name="password"
        type="password"
        label={t("Password")}
        required
      />
    </>
  );
}
function DHIS2Form(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  const [{ url, api_url, username, password }, { updateField }] =
    useConnectionFields(form, [
      { code: "url", name: "Instance" },
      { code: "api_url", name: "API Url" },
      { code: "username", name: "Username" },
      { code: "password", secret: true, name: "Password" },
    ]);

  return (
    <>
      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={url.value}
        name="instance"
        type="url"
        label={t("Instance")}
        required
      />
      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={api_url.value}
        name="api_url"
        type="url"
        label={t("API Url")}
      />

      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={username.value}
        name="username"
        label={t("Username")}
        required
      />

      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={password.value}
        name="password"
        type="password"
        label={t("Password")}
        required
      />
    </>
  );
}
function S3BucketForm(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  const [{ bucket_name, access_key_id, access_key_secret }, { updateField }] =
    useConnectionFields(form, [
      { code: "bucket_name", name: "Bucket name" },
      { code: "access_key_id", name: "Access key ID" },
      { code: "access_key_secret", name: "Secret access key", secret: true },
    ]);

  return (
    <>
      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={bucket_name.value}
        name="bucket_name"
        label={t("Bucket name")}
        required
      />
      <div className="col-span-2">
        <Title level={6}>{t("Credentials")}</Title>
        <p className="text-sm text-gray-500">
          {t(
            "The credentials are required if the bucket cannot be accessed publicly."
          )}
        </p>
      </div>
      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={access_key_id.value}
        name="access_key_id"
        label={t("Access key ID")}
      />

      <Field
        onChange={(event) => updateField(event.target.name, event.target.value)}
        value={access_key_secret.value}
        name="access_key_secret"
        label={t("Secret access key")}
      />
    </>
  );
}
function GCSBucketForm(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  return null;
}

function CustomForm(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  return (
    <div className="col-span-2 space-y-3">
      <Title level={5}>{t("Fields")}</Title>
      <div className="max-h-80 space-y-2 overflow-y-auto py-px px-px">
        {form.formData.fields!.map((field, index) => (
          <div
            key={index}
            className="flex w-full items-center justify-end gap-2"
          >
            <Field
              className="flex-1"
              onChange={(event) =>
                updateFormField(form, index, {
                  code: event.target.value,
                  value: field.value,
                })
              }
              value={field.code}
              name={`code-${index}`}
              pattern="^[a-zA-Z0-9-_]*$"
              label={t("Name")}
              required
            />
            <Field
              name={`value-${index}`}
              label={t("Value")}
              onChange={(event) =>
                updateFormField(form, index, {
                  value: event.target.value,
                  code: field.code,
                })
              }
              value={field.value ?? ""}
              placeholder={t("Text value")}
              required
              className="flex-1"
            />
            <div className="mt-3 flex gap-2">
              <Checkbox
                id={`secret-${index}`}
                className="mt-1"
                name={`secret_${index}`}
                onChange={(event) =>
                  updateFormField(form, index, {
                    code: field.code,
                    secret: event.target.checked,
                  })
                }
                checked={field.secret ?? false}
                label={t("Secret")}
              />
              <button
                type="button"
                onClick={() =>
                  form.setFieldValue(
                    "fields",
                    form.formData.fields!.filter((_, i) => i !== index)
                  )
                }
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <Button
        variant="white"
        size="sm"
        type="button"
        data-testid="add-field"
        onClick={() =>
          form.setFieldValue("fields", [...form.formData.fields!, {}])
        }
        leadingIcon={<PlusCircleIcon className="h-4 w-4" />}
      >
        {t("Add a field")}
      </Button>
    </div>
  );
}

export const CONNECTION_TYPES = {
  [ConnectionType.Postgresql]: {
    label: "PostgreSQL",
    color: "bg-blue-300",
    iconSrc: "/static/connector_postgresql/img/symbol.svg",
    Form: PostgreSQLForm,
  },
  [ConnectionType.Dhis2]: {
    label: "DHIS2 Instance",
    color: "bg-pink-300",
    iconSrc: "/static/connector_dhis2/img/symbol.svg",
    Form: DHIS2Form,
  },
  [ConnectionType.S3]: {
    label: "Amazon S3 Bucket",
    color: "bg-orange-200",
    iconSrc: "/static/connector_s3/img/symbol.svg",
    Form: S3BucketForm,
  },
  [ConnectionType.Gcs]: {
    label: "Google Cloud Bucket",
    color: "bg-blue-200",
    iconSrc: "/static/connector_gcs/img/symbol.svg",
    Form: GCSBucketForm,
  },
  [ConnectionType.Custom]: {
    label: "Custom",
    color: "bg-gray-200",
    iconSrc: null,
    Form: CustomForm,
  },
};

export function convertFieldsToInput(fields: FieldForm[]) {
  return fields.map((f) => ({
    code: f.code,
    secret: Boolean(f.secret),
    value: f.value ?? "",
  }));
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
