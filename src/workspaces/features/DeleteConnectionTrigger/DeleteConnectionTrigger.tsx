import { gql } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { useRouter } from "next/router";
import { ReactElement, useCallback } from "react";
import { useTranslation } from "next-i18next";
import {
  DeleteConnectionTrigger_ConnectionFragment,
  DeleteConnectionTrigger_WorkspaceFragment,
} from "./DeleteConnectionTrigger.generated";
import { deleteConnection } from "workspaces/helpers/connections/utils";

type DeleteConnectionTriggerProps = {
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  confirmMessage?: string;
  connection: DeleteConnectionTrigger_ConnectionFragment;
  workspace: DeleteConnectionTrigger_WorkspaceFragment;
};

const DeleteConnectionTrigger = (props: DeleteConnectionTriggerProps) => {
  const { t } = useTranslation();
  const {
    connection,
    workspace,
    children,
    confirmMessage = t(
      'Are you sure you want to delete the connection "{{name}}"?',
      {
        name: connection.name,
      },
    ),
  } = props;
  const router = useRouter();

  const clearCache = useCacheKey("connections");

  const onClick = useCallback(async () => {
    if (
      window.confirm(confirmMessage) &&
      (await deleteConnection(connection.id))
    ) {
      router.push({
        pathname: "/workspaces/[workspaceSlug]/connections",
        query: { workspaceSlug: workspace.slug },
      });
      clearCache();
    }
  }, [connection, clearCache, router, workspace, confirmMessage]);

  if (!connection.permissions.delete) {
    return null;
  }
  return children({ onClick });
};

DeleteConnectionTrigger.fragments = {
  workspace: gql`
    fragment DeleteConnectionTrigger_workspace on Workspace {
      slug
    }
  `,
  connection: gql`
    fragment DeleteConnectionTrigger_connection on Connection {
      id
      name
      permissions {
        delete
      }
    }
  `,
};

export default DeleteConnectionTrigger;
