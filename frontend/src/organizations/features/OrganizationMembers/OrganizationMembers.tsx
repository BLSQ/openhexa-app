import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import useCacheKey from "core/hooks/useCacheKey";
import useDebounce from "core/hooks/useDebounce";
import SearchInput from "core/features/SearchInput";
import { User, OrganizationMembership } from "graphql/types";
import { DateTime } from "luxon";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import DeleteOrganizationMemberDialog from "./DeleteOrganizationMemberDialog";
import UpdateOrganizationMemberDialog from "./UpdateOrganizationMemberDialog";
import useMe from "identity/hooks/useMe";
import { formatOrganizationMembershipRole } from "organizations/helpers/organization";
import { formatWorkspaceMembershipRole } from "workspaces/helpers/workspace";
import { useOrganizationMembersQuery } from "./OrganizationMembers.generated";

const DEFAULT_PAGE_SIZE = 10;

type OrganizationMember = Pick<
  OrganizationMembership,
  "id" | "role" | "workspaceMemberships"
> & {
  user: Pick<User, "id" | "displayName" | "email">;
};

export default function OrganizationMembers({
  organizationId,
}: {
  organizationId: string;
}) {
  const me = useMe();
  const { t } = useTranslation();
  const [selectedMember, setSelectedMember] = useState<OrganizationMember>();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const { data, refetch, loading } = useOrganizationMembersQuery({
    variables: {
      id: organizationId,
      page: 1,
      perPage: DEFAULT_PAGE_SIZE,
      term: debouncedSearchTerm || undefined,
    },
    fetchPolicy: "cache-and-network",
  });

  useCacheKey("organization", () => refetch());

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      page,
      id: organizationId,
      term: debouncedSearchTerm || undefined,
    }).then();
  };

  if (!data?.organization) {
    return null;
  }

  const { organization } = data;

  const handleDeleteClicked = (member: OrganizationMember) => {
    setSelectedMember(member);
    setOpenDeleteDialog(true);
  };

  const handleUpdateClicked = (member: OrganizationMember) => {
    setSelectedMember(member);
    setOpenEditDialog(true);
  };

  const formatWorkspaceRoles = (
    workspaceMemberships: OrganizationMember["workspaceMemberships"],
  ) => {
    if (!workspaceMemberships || workspaceMemberships.length === 0) {
      return t("No workspace access");
    }

    return workspaceMemberships
      .map(
        (membership) =>
          `${membership.workspace.name}: ${formatWorkspaceMembershipRole(membership.role)}`,
      )
      .join(", ");
  };

  return (
    <>
      <div className="mb-4">
        <SearchInput
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={t("Search members...")}
          loading={loading}
          className="max-w-md"
        />
      </div>
      <DataGrid
        className="bg-white shadow-md"
        defaultPageSize={DEFAULT_PAGE_SIZE}
        totalItems={organization.members.totalItems}
        fixedLayout={false}
        data={organization.members.items}
        fetchData={onChangePage}
      >
        <TextColumn
          className="max-w-[20ch] py-3"
          accessor={({ user }) => user.displayName}
          id="name"
          label={t("Name")}
          defaultValue="-"
        />
        <TextColumn
          className="max-w-[25ch] py-3"
          accessor={({ user }) => user.email}
          id="email"
          label={t("Email")}
        />
        <TextColumn
          className="max-w-[15ch] py-3"
          accessor={(member) => formatOrganizationMembershipRole(member.role)}
          label={t("Organization Role")}
          id="org_role"
        />
        <TextColumn
          className="max-w-[40ch] py-3"
          accessor={(member) =>
            formatWorkspaceRoles(member.workspaceMemberships)
          }
          label={t("Workspace Roles")}
          id="workspace_roles"
        />
        <DateColumn
          className="max-w-[15ch] py-3"
          accessor="createdAt"
          id="createdAt"
          label={t("Joined")}
          format={DateTime.DATE_FULL}
        />
        {organization.permissions.manageMembers && (
          <BaseColumn className="flex justify-end gap-x-2">
            {(member) =>
              me.user?.id !== member.user.id ? (
                <>
                  <Button
                    onClick={() => handleUpdateClicked(member)}
                    size="sm"
                    variant="secondary"
                  >
                    <PencilIcon className="h-4" />
                  </Button>
                  <Button
                    onClick={() => handleDeleteClicked(member)}
                    size="sm"
                    variant="secondary"
                  >
                    <TrashIcon className="h-4" />
                  </Button>
                </>
              ) : (
                <></>
              )
            }
          </BaseColumn>
        )}
      </DataGrid>
      {selectedMember && (
        <DeleteOrganizationMemberDialog
          open={openDeleteDialog}
          onClose={() => {
            setSelectedMember(undefined);
            setOpenDeleteDialog(false);
          }}
          member={selectedMember}
        />
      )}
      {selectedMember && (
        <UpdateOrganizationMemberDialog
          open={openEditDialog}
          onClose={() => {
            setSelectedMember(undefined);
            setOpenEditDialog(false);
          }}
          member={selectedMember}
        />
      )}
    </>
  );
}
