import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import Block from "core/components/Block";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import { BaseColumn } from "core/components/DataGrid";
import DataGrid from "core/components/DataGrid/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Link from "core/components/Link";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import BackLayout from "core/layouts/back";
import { WorkspaceInvitation, WorkspaceInvitationStatus } from "graphql/types";
import {
  AccountPageDocument,
  AccountPageQuery,
  useAccountPageQuery,
} from "identity/graphql/queries.generated";
import { logout } from "identity/helpers/auth";
import { useTranslation } from "next-i18next";
import {
  useDeclineWorkspaceInvitationMutation,
  useJoinWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import { formatWorkspaceMembershipRole } from "workspaces/helpers/workspace";
import { toast } from "react-toastify";
import AccountProfileSettings from "identity/features/AccountProfileSettings";
import AccountSecuritySettings from "identity/features/AccountSecuritySettings";
import AccountAiSettings from "identity/features/AccountAiSettings";

function AccountPage() {
  const { t } = useTranslation();
  const { data, refetch } = useAccountPageQuery();

  const [joinWorkspace] = useJoinWorkspaceMutation();
  const [declineWorkspaceInvitation] = useDeclineWorkspaceInvitationMutation();

  async function doJoinWorkspace(invitation: WorkspaceInvitation) {
    const { data } = await joinWorkspace({
      variables: { input: { invitationId: invitation.id } },
    });
    if (!data?.joinWorkspace.success) {
      toast.error(t("Failed to accept invitation"));
    }
  }

  async function doDeclineWorkspaceInvitation(invitation: WorkspaceInvitation) {
    if (
      !window.confirm(t("Are you sure you want to decline this invitation?"))
    ) {
      return;
    }
    const { data } = await declineWorkspaceInvitation({
      variables: { input: { invitationId: invitation.id } },
    });
    if (!data?.declineWorkspaceInvitation.success) {
      toast.error(t("Failed to decline invitation"));
    }
  }

  if (!data?.me.user) {
    return null;
  }

  const { user } = data.me;
  return (
    <Page title={t("Account")}>
      <BackLayout
        className="gap-5 flex flex-col"
        title={
          <div className={"flex justify-between items-center gap-3"}>
            {t("Your account")}
            <Button
              variant="primary"
              onClick={() => logout()}
              leadingIcon={<ArrowRightOnRectangleIcon className="h-4 w-4" />}
            >
              {t("Logout")}
            </Button>
          </div>
        }
      >
        <DataCard item={user} className="divide-y divide-gray-100">
          <AccountProfileSettings user={user} />
          <AccountSecuritySettings hasTwoFactorEnabled={data.me.hasTwoFactorEnabled} />
          <AccountAiSettings refetch={refetch} settings={user.aiSettings}/>
        </DataCard>

        {data.pendingWorkspaceInvitations.totalItems > 0 ? (
          <Block>
            <Block.Header>{t("Workspace invitations")}</Block.Header>
            <DataGrid
              totalItems={data.pendingWorkspaceInvitations.totalItems}
              data={data.pendingWorkspaceInvitations.items}
              fixedLayout={false}
            >
              <TextColumn
                accessor="workspace.name"
                label={t("Workspace")}
                id="workspace"
              />
              <TextColumn
                accessor="invitedBy.displayName"
                label={t("Invited by")}
                id="invitedBy"
              />
              <TextColumn
                accessor={(member) =>
                  formatWorkspaceMembershipRole(member.role)
                }
                label={t("Role")}
                id="role"
              />
              <BaseColumn className="flex justify-end gap-x-2">
                {(invitation) => (
                  <>
                    {invitation.status ===
                      WorkspaceInvitationStatus.Declined && (
                      <span className="text-sm text-gray-400">
                        {t("Declined")}
                      </span>
                    )}

                    {invitation.status ===
                      WorkspaceInvitationStatus.Accepted && (
                      <Link
                        href={{
                          pathname: "/workspaces/[workspaceSlug]",
                          query: { workspaceSlug: invitation.workspace.slug },
                        }}
                        className="text-sm"
                      >
                        {t("View")}
                      </Link>
                    )}
                    {invitation.status ===
                      WorkspaceInvitationStatus.Pending && (
                      <>
                        <Button
                          onClick={() =>
                            doDeclineWorkspaceInvitation(invitation)
                          }
                          size="sm"
                          variant="danger"
                        >
                          {t("Decline")}
                        </Button>
                        <Button
                          onClick={() => doJoinWorkspace(invitation)}
                          size="sm"
                        >
                          {t("Accept")}
                        </Button>
                      </>
                    )}
                  </>
                )}
              </BaseColumn>
            </DataGrid>
          </Block>
        ) : null}
      </BackLayout>
    </Page>
  );
}

AccountPage.getLayout = (page: any) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query<AccountPageQuery>({
      query: AccountPageDocument,
    });
    if (!data.me.user) {
      return {
        notFound: true,
      };
    }
  },
});

export default AccountPage;
