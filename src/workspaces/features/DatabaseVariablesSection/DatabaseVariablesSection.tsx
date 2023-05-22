import { gql } from "@apollo/client";
import { DatabaseVariablesSection_WorkspaceFragment } from "./DatabaseVariablesSection.generated";
import { useTranslation } from "react-i18next";
import { useMemo } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { slugify } from "workspaces/helpers/connection";
import SecretField from "./SecretField";
import ClipboardButton from "core/components/ClipboardButton";

type DatabaseVariablesSectionProps = {
  workspace: DatabaseVariablesSection_WorkspaceFragment;
};

const DatabaseVariablesSection = (props: DatabaseVariablesSectionProps) => {
  const { t } = useTranslation();
  const {
    database: { credentials },
  } = props.workspace;
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
    [credentials]
  );
  return (
    <DataGrid
      className="max-2w-lg w-3/4 rounded-md border"
      data={dbCredentials}
      fixedLayout={true}
    >
      <TextColumn className="py-3" label={t("Name")} accessor="name" />
      <BaseColumn label={t("Environment variable")} accessor="name">
        {(value) => (
          <code className="rounded-md bg-slate-100 p-1.5 font-mono text-xs font-medium text-gray-600">
            {slugify(`WORKSPACE_DATABASE_${value}`)}
          </code>
        )}
      </BaseColumn>
      <BaseColumn className="flex gap-x-2 text-gray-900" label={t("Value")}>
        {(field) => (
          <div className="flex  gap-x-1 truncate">
            {field.secret && field.value && <SecretField value={field.value} />}
            {!field.secret && (
              <>
                {field.value}
                <ClipboardButton value={field.value} />
              </>
            )}
          </div>
        )}
      </BaseColumn>
    </DataGrid>
  );
};

DatabaseVariablesSection.fragment = {
  workspace: gql`
    fragment DatabaseVariablesSection_workspace on Workspace {
      slug
      database {
        credentials {
          dbName
          username
          password
          host
          port
          url
        }
      }
    }
  `,
};

export default DatabaseVariablesSection;
