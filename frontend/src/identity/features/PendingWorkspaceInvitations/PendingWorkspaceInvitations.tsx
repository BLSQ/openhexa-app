import Block from "core/components/Block";
import Button from "core/components/Button";
import { BaseColumn } from "core/components/DataGrid";
import DataGrid from "core/components/DataGrid/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Link from "core/components/Link";
import { WorkspaceInvitation, WorkspaceInvitationPage, WorkspaceInvitationStatus } from "graphql/types";
import {
  useDeclineWorkspaceInvitationMutation,
  useJoinWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";
import { formatWorkspaceMembershipRole } from "workspaces/helpers/workspace";
import { toast } from "react-toastify";
import { t } from "i18next";


type PendingWorkspaceInvitationsProps = {
  invitations: WorkspaceInvitationPage
}

const PendingWorkspaceInvitations = (props: PendingWorkspaceInvitationsProps) => {
  const { invitations } = props;

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

  return (
    invitations.totalItems > 0 ? (
      <Block>
        <Block.Header>{t("Workspace invitations")}</Block.Header>
        <DataGrid
          totalItems={invitations.totalItems}
          data={invitations.items}
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
    ) : null
  );
}

export default PendingWorkspaceInvitations;
