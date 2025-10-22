import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import useCacheKey from "core/hooks/useCacheKey";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { WorkspaceInvitation } from "graphql/types";
import Button from "core/components/Button/Button";
import { ArrowPathIcon, TrashIcon } from "@heroicons/react/24/outline";
import { useState } from "react";
import DeleteWorkspaceInvitationDialog from "workspaces/features/WorkspaceInvitations/DeleteWorkspaceInvitationDialog";
import ResendWorkspaceInvitationDialog from "workspaces/features/WorkspaceInvitations/ResendWorkspaceInvitationDialog";
import WorkspaceRoleBadge from "workspaces/components/WorkspaceRoleBadge";
import Block from "core/components/Block";
import { useQuery } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const OrganizationWorkspaceInvitationsDoc = graphql(`
query OrganizationWorkspaceInvitations($id: UUID!, $page: Int, $perPage: Int) {
  organization(id: $id) {
    id
    permissions {
      manageMembers
    }
    pendingWorkspaceInvitations(page: $page, perPage: $perPage) {
      totalItems
      items {
        id
        email
        role
        status
        workspace {
          name
          slug
        }
        invitedBy {
          displayName
        }
        createdAt
      }
    }
  }
}
`);

const DEFAULT_PAGE_SIZE = 5;

type Invitation = Pick<WorkspaceInvitation, "id" | "email">;

export default function OrganizationWorkspaceInvitations({
  organizationId,
}: {
  organizationId: string;
}) {
  const { t } = useTranslation();
  const [selectedInvitation, setSelectedInvitation] = useState<Invitation>();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openResendDialog, setOpenResendDialog] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { data, refetch } = useQuery(OrganizationWorkspaceInvitationsDoc, {
    variables: {
      id: organizationId,
      page: 1,
      perPage: DEFAULT_PAGE_SIZE,
    },
  });

  useCacheKey("organization", () => refetch());

  const onChangePage = ({ page }: { page: number }) => {
    setIsLoading(true);
    refetch({
      page,
      id: organizationId,
    }).finally(() => {
      setIsLoading(false);
    });
  };

  if (!data?.organization) {
    return null;
  }

  const { pendingWorkspaceInvitations, permissions } = data.organization;

  const handleDeleteClicked = (invitationId: string) => {
    const invitation = pendingWorkspaceInvitations.items.filter(
      (x) => x.id === invitationId,
    )[0];
    setSelectedInvitation(invitation);
    setOpenDeleteDialog(true);
  };

  const handleResendClicked = (invitationId: string) => {
    const invitation = pendingWorkspaceInvitations.items.filter(
      (x) => x.id === invitationId,
    )[0];
    setSelectedInvitation(invitation);
    setOpenResendDialog(true);
  };

  return (
    <Block>
      <DataGrid
        defaultPageSize={DEFAULT_PAGE_SIZE}
        totalItems={pendingWorkspaceInvitations.totalItems}
        fixedLayout={true}
        data={pendingWorkspaceInvitations.items}
        fetchData={onChangePage}
        emptyLabel={t("No workspace invitations")}
        className="min-h-30"
        loading={isLoading}
      >
        <BaseColumn label={t("Email")} id="email" minWidth={350}>
          {(invitation) => (
            <div>
              <div className="font-medium">{invitation.email}</div>
              <div className="text-xs text-gray-400">
                {invitation.invitedBy?.displayName
                  ? t("Invited by {{name}}", {
                      name: invitation.invitedBy.displayName,
                    })
                  : t("Invited")}
              </div>
            </div>
          )}
        </BaseColumn>
        <BaseColumn label={t("Workspace Role")} id="role">
          {(invitation) => (
            <WorkspaceRoleBadge
              workspaceName={invitation.workspace.name}
              role={invitation.role}
              size="sm"
            />
          )}
        </BaseColumn>
        <DateColumn
          className="py-4"
          accessor="createdAt"
          id="createdAt"
          label={t("Date sent")}
          format={DateTime.DATE_FULL}
        />
        {permissions.manageMembers && (
          <BaseColumn className="flex justify-end gap-x-2">
            {(invitation) => (
              <>
                <Button
                  onClick={() => handleResendClicked(invitation.id)}
                  size="sm"
                  variant="secondary"
                >
                  <ArrowPathIcon className="h-4" />
                </Button>
                <Button
                  onClick={() => handleDeleteClicked(invitation.id)}
                  size="sm"
                  variant="secondary"
                >
                  <TrashIcon className="h-4" />
                </Button>
              </>
            )}
          </BaseColumn>
        )}
      </DataGrid>
      {selectedInvitation && (
        <DeleteWorkspaceInvitationDialog
          invitation={selectedInvitation}
          open={openDeleteDialog}
          onClose={() => {
            setSelectedInvitation(undefined);
            setOpenDeleteDialog(false);
          }}
        />
      )}
      {selectedInvitation && (
        <ResendWorkspaceInvitationDialog
          invitation={selectedInvitation}
          open={openResendDialog}
          onClose={() => {
            setSelectedInvitation(undefined);
            setOpenResendDialog(false);
          }}
        />
      )}
    </Block>
  );
}
