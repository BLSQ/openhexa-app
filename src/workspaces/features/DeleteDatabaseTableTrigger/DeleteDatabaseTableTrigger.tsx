import { gql } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { useRouter } from "next/router";
import { ReactElement, useCallback } from "react";
import { useTranslation } from "next-i18next";
import {
  DatabaseTableDeleteTrigger_DatabaseFragment,
  DatabaseTableDeleteTrigger_WorkspaceFragment,
} from "./DeleteDatabaseTableTrigger.generated";
import { deleteTable } from "workspaces/helpers/database";

type DeleteDatabaseTableTriggerProps = {
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  confirmMessage?: string;
  table: DatabaseTableDeleteTrigger_DatabaseFragment;
  workspace: DatabaseTableDeleteTrigger_WorkspaceFragment;
};

const DeleteDatabaseTableTrigger = (props: DeleteDatabaseTableTriggerProps) => {
  const { t } = useTranslation();
  const {
    table,
    workspace,
    children,
    confirmMessage = t('Are you sure you want to delete table "{{name}}"?', {
      name: table.name,
    }),
  } = props;
  const router = useRouter();

  const clearCache = useCacheKey("connections");

  const onClick = useCallback(async () => {
    if (
      window.confirm(confirmMessage) &&
      (await deleteTable(workspace.slug, table.name))
    ) {
      router.push({
        pathname: "/workspaces/[workspaceSlug]/databases",
        query: { workspaceSlug: workspace.slug },
      });
      clearCache();
    }
  }, [table, clearCache, router, workspace, confirmMessage]);

  if (!workspace.permissions.deleteDatabaseTable) {
    return null;
  }
  return children({ onClick });
};

DeleteDatabaseTableTrigger.fragments = {
  workspace: gql`
    fragment DatabaseTableDeleteTrigger_workspace on Workspace {
      slug
      permissions {
        deleteDatabaseTable
      }
    }
  `,
  table: gql`
    fragment DatabaseTableDeleteTrigger_database on DatabaseTable {
      name
    }
  `,
};

export default DeleteDatabaseTableTrigger;
