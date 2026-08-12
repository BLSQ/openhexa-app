import Block from "core/components/Block";
import { BaseColumn } from "core/components/DataGrid";
import DataGrid from "core/components/DataGrid/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Link from "core/components/Link";
import { CustomApolloClient } from "core/helpers/apollo";
import {
  AccountAccessTokensDocument,
  AccountAccessTokensQuery,
  useAccountAccessTokensQuery,
} from "identity/graphql/queries.generated";
import { Trans, useTranslation } from "next-i18next";
import React, { useState } from "react";
import { formatWorkspaceMembershipRole } from "workspaces/helpers/workspace";
import WorkspaceAccessToken from "workspaces/features/WorkspaceAccessToken";

// A page costs only the workspaces that exist, so a generous default is free for
// the many users with a handful of workspaces and saves paging for the few with
// dozens. Those few can go further with the page size selector.
const DEFAULT_PAGE_SIZE = 20;
const PAGE_SIZE_OPTIONS = [20, 50, 100];

type WorkspaceItem = AccountAccessTokensQuery["workspaces"]["items"][number];

const AccountAccessTokens = () => {
  const { t } = useTranslation();
  const [pagination, setPagination] = useState({
    page: 1,
    perPage: DEFAULT_PAGE_SIZE,
  });

  const { data, previousData } = useAccountAccessTokensQuery({
    variables: pagination,
  });

  const onFetchData: React.ComponentProps<typeof DataGrid>["fetchData"] = ({
    page,
    pageSize,
  }) => {
    setPagination({ page, perPage: pageSize });
  };

  // previousData keeps the current page visible while the next one loads
  const workspaces = (data ?? previousData)?.workspaces;
  if (!workspaces || workspaces.totalItems === 0) {
    return null;
  }

  return (
    <Block>
      <Block.Header>{t("Access tokens")}</Block.Header>
      <Block.Content className="space-y-4">
        <p className="text-sm text-gray-500">
          <Trans>
            Use these tokens to authenticate with the <code>openhexa</code> CLI
            and the OpenHEXA SDK. You have one token per workspace. See the{" "}
            <Link
              target="_blank"
              href="https://docs.openhexa.com/writing-pipelines/"
            >
              documentation
            </Link>{" "}
            to get started.
          </Trans>
        </p>
        <DataGrid
          totalItems={workspaces.totalItems}
          data={workspaces.items}
          defaultPageSize={DEFAULT_PAGE_SIZE}
          pageSizeOptions={PAGE_SIZE_OPTIONS}
          fetchData={onFetchData}
          fixedLayout={false}
        >
          <TextColumn accessor="name" label={t("Workspace")} id="workspace" />
          <TextColumn
            accessor={(workspace: WorkspaceItem) =>
              workspace.currentMembership
                ? formatWorkspaceMembershipRole(
                    workspace.currentMembership.role,
                  )
                : "-"
            }
            label={t("Role")}
            id="role"
          />
          <BaseColumn label={t("Token")} id="token" className="w-1/2 min-w-64">
            {(workspace: WorkspaceItem) => (
              <WorkspaceAccessToken
                workspaceSlug={workspace.slug}
                canGenerate={workspace.permissions.generateToken}
              />
            )}
          </BaseColumn>
        </DataGrid>
      </Block.Content>
    </Block>
  );
};

AccountAccessTokens.prefetch = async (client: CustomApolloClient) =>
  client.query({
    query: AccountAccessTokensDocument,
    variables: { page: 1, perPage: DEFAULT_PAGE_SIZE },
  });

export default AccountAccessTokens;
