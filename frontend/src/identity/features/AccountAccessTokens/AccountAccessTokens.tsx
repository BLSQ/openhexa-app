import Block from "core/components/Block";
import { BaseColumn } from "core/components/DataGrid";
import DataGrid from "core/components/DataGrid/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Link from "core/components/Link";
import { AccountPageQuery } from "identity/graphql/queries.generated";
import { Trans, useTranslation } from "next-i18next";
import { formatWorkspaceMembershipRole } from "workspaces/helpers/workspace";
import WorkspaceAccessToken from "workspaces/features/WorkspaceAccessToken";

type AccountAccessTokensProps = {
  workspaces: AccountPageQuery["workspaces"];
};

type WorkspaceItem = AccountPageQuery["workspaces"]["items"][number];

const AccountAccessTokens = (props: AccountAccessTokensProps) => {
  const { workspaces } = props;
  const { t } = useTranslation();

  if (workspaces.totalItems === 0) {
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
          totalItems={workspaces.items.length}
          data={workspaces.items}
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
          <BaseColumn label={t("Token")} id="token">
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

export default AccountAccessTokens;
