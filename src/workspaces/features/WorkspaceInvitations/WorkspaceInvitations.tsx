import { gql, useQuery } from "@apollo/client";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import useCacheKey from "core/hooks/useCacheKey";
import { capitalize } from "lodash";
import { DateTime } from "luxon";
import { useTranslation } from "react-i18next";
import { WorskspaceInvitationsQuery } from "./WorkspaceInvitations.generated";
import { WorkspaceInvitation, WorkspaceInvitationStatus } from "graphql-types";
import Button from "core/components/Button/Button";
import { ArrowPathIcon, TrashIcon } from "@heroicons/react/24/outline";
import { useState } from "react";
import DeleteWorkspaceInvitationDialog from "./DeleteWorkspaceInvitationDialog";
import ResendWorkspaceInvitationDialog from "./ResendWorkspaceInvitationDialog";

const DEFAULT_PAGE_SIZE = 5;

type Invitation = Pick<WorkspaceInvitation, "id" | "email">;

export default function WorkspaceInvitations({
  workspaceSlug,
}: {
  workspaceSlug: string;
}) {
  const { t } = useTranslation();
  const [selectedInvitation, setSelectedInvitation] = useState<Invitation>();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openResendDialog, setOpenResendDialog] = useState(false);

  const { data, refetch } = useQuery<WorskspaceInvitationsQuery>(
    gql`
      query WorskspaceInvitations(
        $slug: String!
        $status: WorkspaceInvitationStatus
        $page: Int
        $perPage: Int
      ) {
        workspace(slug: $slug) {
          slug
          permissions {
            manageMembers
          }
          invitations(status: $status, page: $page, perPage: $perPage) {
            totalItems
            items {
              id
              role
              email
              status
              invited_by {
                displayName
              }
              createdAt
            }
          }
        }
      }
    `,
    {
      variables: {
        slug: workspaceSlug,
        status: WorkspaceInvitationStatus.Pending,
        page: 1,
        perPage: DEFAULT_PAGE_SIZE,
      },
    },
  );

  useCacheKey("workspace", () => refetch());

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      page,
      slug: workspaceSlug,
    });
  };

  if (!data?.workspace) {
    return null;
  }
  const { invitations } = data.workspace;

  const handleDeleteClicked = (invitationId: string) => {
    const invitation = invitations.items.filter(
      (x) => x.id === invitationId,
    )[0];
    setSelectedInvitation(invitation);
    setOpenDeleteDialog(true);
  };

  const handleResendClicked = (invitationId: string) => {
    const invitation = invitations.items.filter(
      (x) => x.id === invitationId,
    )[0];
    setSelectedInvitation(invitation);
    setOpenResendDialog(true);
  };

  const { workspace } = data;

  return (
    <>
      <DataGrid
        className="bg-white shadow-md"
        defaultPageSize={DEFAULT_PAGE_SIZE}
        totalItems={invitations.totalItems}
        fixedLayout={false}
        data={invitations.items}
        fetchData={onChangePage}
      >
        <TextColumn
          className="max-w-[20ch] py-3 "
          accessor="email"
          id="email"
          label={t("Email")}
          defaultValue="-"
        />
        <TextColumn
          className="max-w-[20ch] py-3 "
          accessor={(member) => capitalize(member.role)}
          label={t("Role")}
          id="member_role"
        />
        <TextColumn
          className="max-w-[20ch] py-3 "
          accessor={(invitation) => invitation.invited_by.displayName}
          label={t("Invited by")}
          id="invited_by"
        />
        <DateColumn
          className="max-w-[20ch] py-3 "
          accessor="createdAt"
          id="createdAt"
          label={t("Date sent")}
          format={DateTime.DATE_FULL}
        />
        {workspace.permissions.manageMembers && (
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
    </>
  );
}
