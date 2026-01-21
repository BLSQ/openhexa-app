import { gql } from "@apollo/client";
import { DatabaseVariablesSection_CredentialsFragment } from "./DatabaseVariablesSection.generated";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import SecretField from "./SecretField";
import Clipboard from "core/components/Clipboard";
import { slugify } from "workspaces/helpers/connections/utils";

type DatabaseVariablesSectionProps = {
  credentials: DatabaseVariablesSection_CredentialsFragment | null | undefined;
};

const DatabaseVariablesSection = ({
  credentials,
}: DatabaseVariablesSectionProps) => {
  const { t } = useTranslation();

  const dbCredentials = useMemo(
    () => [
      {
        name: "db_name",
        value: credentials?.dbName,
        secret: false,
      },
      {
        name: "username",
        value: credentials?.username,
        secret: false,
      },
      {
        name: "password",
        value: credentials?.password,
        secret: true,
      },
      {
        name: "port",
        value: credentials?.port,
        secret: false,
      },
      {
        name: "host",
        value: credentials?.host,
        secret: false,
      },
      {
        name: "url",
        value: credentials?.url,
        secret: true,
      },
    ],
    [credentials],
  );
  return (
    <DataGrid
      className="rounded-md border"
      data={dbCredentials}
      fixedLayout={true}
    >
      <TextColumn
        className="py-3 font-mono"
        label={t("Name")}
        accessor="name"
        width={100}
      />
      <BaseColumn label={t("Environment variable")} accessor="name" width={150}>
        {(value) => (
          <Clipboard value={slugify(`WORKSPACE_DATABASE_${value}`)}>
            <code className="rounded-md bg-slate-100 p-1.5 font-mono text-xs font-medium text-gray-600">
              {slugify(`WORKSPACE_DATABASE_${value}`)}
            </code>
          </Clipboard>
        )}
      </BaseColumn>
      <BaseColumn
        className="flex gap-x-1.5 font-mono text-gray-900"
        label={t("Value")}
        width={400}
      >
        {(field) => (
          <div className="flex gap-x-1">
            {field.secret && field.value && <SecretField value={field.value} />}
            {!field.secret && (
              <Clipboard value={field.value}>
                <span>{field.value}</span>
              </Clipboard>
            )}
          </div>
        )}
      </BaseColumn>
    </DataGrid>
  );
};

DatabaseVariablesSection.fragments = {
  credentials: gql`
    fragment DatabaseVariablesSection_credentials on DatabaseCredentials {
      dbName
      username
      password
      host
      port
      url
    }
  `,
};

export default DatabaseVariablesSection;
