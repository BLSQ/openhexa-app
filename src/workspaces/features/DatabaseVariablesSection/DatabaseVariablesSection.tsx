import { gql } from "@apollo/client";
import { DatabaseVariablesSection_WorkspaceFragment } from "./DatabaseVariablesSection.generated";
import { useTranslation } from "react-i18next";
import { useCallback, useMemo, useState } from "react";
import {
  EyeIcon,
  EyeSlashIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { slugify } from "workspaces/helpers/connection";

type DatabaseVariablesSectionProps = {
  workspace: DatabaseVariablesSection_WorkspaceFragment;
};
const SecretField = (field: { value: string | number }) => {
  const { value } = field;
  const [showSecret, setShowSecret] = useState<boolean>(false);
  const toggleSecret = useCallback(
    () => setShowSecret((showSecet) => !showSecet),
    []
  );

  if (showSecret) {
    return (
      <p className="flex justify-start gap-x-2">
        <span className="text-sm text-gray-900">{value}</span>
        <button
          onClick={toggleSecret}
          type="button"
          className="cursor-pointer gap-1 hover:text-blue-500 focus:outline-none"
        >
          <EyeSlashIcon className="h-3.5 w-3.5" />
        </button>
      </p>
    );
  }

  return (
    <p className="flex items-center justify-start gap-x-2">
      <span>*********</span>
      <button
        onClick={toggleSecret}
        type="button"
        className="flex cursor-pointer gap-1 hover:text-blue-500 focus:outline-none"
      >
        <EyeIcon className="h-3.5 w-3.5" />
      </button>
    </p>
  );
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
      <BaseColumn
        className="flex items-center gap-x-2 text-gray-900"
        label={t("Value")}
      >
        {(field) => (
          <>
            {field.secret && <LockClosedIcon className="h-3 w-3" />}
            {field.secret && field.value && <SecretField value={field.value} />}
            {!field.secret && field.value}
          </>
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
