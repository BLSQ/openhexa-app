import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import useCacheKey from "core/hooks/useCacheKey";
import capitalize from "lodash/capitalize";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useOrganizationInvitationsQuery } from "./OrganizationInvitations.generated";
import {
  OrganizationInvitation,
  OrganizationInvitationStatus,
} from "graphql/types";
import Button from "core/components/Button/Button";
import { ArrowPathIcon, TrashIcon } from "@heroicons/react/24/outline";
import { useCallback, useState } from "react";
import DeleteOrganizationInvitationDialog from "./DeleteOrganizationInvitationDialog";
import ResendOrganizationInvitationDialog from "./ResendOrganizationInvitationDialog";
import Block from "core/components/Block";

const DEFAULT_PAGE_SIZE = 5;

type Invitation = Pick<OrganizationInvitation, "id" | "email">;

export default function OrganizationInvitations({
  organizationId,
}: {
  organizationId: string;
}) {
  const { t } = useTranslation();
  const [selectedInvitation, setSelectedInvitation] = useState<Invitation>();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openResendDialog, setOpenResendDialog] = useState(false);

  const { data, refetch, loading } = useOrganizationInvitationsQuery({
    variables: {
      id: organizationId,
      page: 1,
      perPage: DEFAULT_PAGE_SIZE,
    },
  });

  useCacheKey("organization", () => refetch());

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      page,
      id: organizationId,
    }).then();
  };

  const formatInvitationStatus = useCallback(
    (status: OrganizationInvitationStatus) => {
      switch (status) {
        case OrganizationInvitationStatus.Pending:
          return t("Pending");
        case OrganizationInvitationStatus.Accepted:
          return t("Accepted");
        case OrganizationInvitationStatus.Declined:
          return t("Declined");
      }
    },
    [t],
  );

  const invitations = data?.organization?.invitations ?? {
    items: [],
    totalItems: 0,
  };
  const organization = data?.organization ?? {
    permissions: {
      manageMembers: false,
    },
  };

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

  return (
    <Block>
      <DataGrid
        defaultPageSize={DEFAULT_PAGE_SIZE}
        totalItems={invitations.totalItems}
        fixedLayout={false}
        data={invitations.items}
        fetchData={onChangePage}
        emptyLabel={t("No pending invitations")}
        loading={loading}
        className="min-h-30"
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
          accessor={(invitation) => invitation.invitedBy?.displayName || "-"}
          label={t("Invited by")}
          id="invitedBy"
        />
        <DateColumn
          className="max-w-[20ch] py-3 "
          accessor="createdAt"
          id="createdAt"
          label={t("Date sent")}
          format={DateTime.DATE_FULL}
        />
        <BaseColumn<OrganizationInvitationStatus>
          id="status"
          accessor="status"
          label={t("Status")}
        >
          {(value) => <span>{formatInvitationStatus(value)}</span>}
        </BaseColumn>
        {organization.permissions.manageMembers && (
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
        <DeleteOrganizationInvitationDialog
          invitation={selectedInvitation}
          open={openDeleteDialog}
          onClose={() => {
            setSelectedInvitation(undefined);
            setOpenDeleteDialog(false);
          }}
        />
      )}
      {selectedInvitation && (
        <ResendOrganizationInvitationDialog
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
