import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import useCacheKey from "core/hooks/useCacheKey";
import useDebounce from "core/hooks/useDebounce";
import SearchInput from "core/features/SearchInput";
import { User as UserType, OrganizationMembership } from "graphql/types";
import { DateTime } from "luxon";
import { useState, useEffect } from "react";
import { useTranslation } from "next-i18next";
import DeleteOrganizationMemberDialog from "./DeleteOrganizationMemberDialog";
import UpdateOrganizationMemberDialog from "./UpdateOrganizationMemberDialog";
import useMe from "identity/hooks/useMe";
import {
  useOrganizationMembersQuery,
  OrganizationMembersQuery,
} from "./OrganizationMembers.generated";
import Block from "core/components/Block";
import User from "core/features/User";
import OrganizationRoleBadge from "organizations/components/OrganizationRoleBadge";
import WorkspaceRolesList from "organizations/components/WorkspaceRolesList";

const DEFAULT_PAGE_SIZE = 10;

type OrganizationMember = Pick<
  OrganizationMembership,
  "id" | "role" | "workspaceMemberships"
> & {
  user: Pick<UserType, "id" | "displayName" | "email">;
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
  const [previousData, setPreviousData] =
    useState<OrganizationMembersQuery | null>(null);

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

  useEffect(() => {
    if (data && !loading) {
      setPreviousData(data);
    }
  }, [data, loading]);

  useCacheKey("organization", () => refetch());

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      page,
      id: organizationId,
      term: debouncedSearchTerm || undefined,
    }).then();
  };

  const displayData = data || previousData;
  const organization = displayData?.organization ?? {
    members: { items: [], totalItems: 0 },
    permissions: { manageMembers: false },
  };

  const handleDeleteClicked = (member: OrganizationMember) => {
    setSelectedMember(member);
    setOpenDeleteDialog(true);
  };

  const handleUpdateClicked = (member: OrganizationMember) => {
    setSelectedMember(member);
    setOpenEditDialog(true);
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
          fitWidth
        />
      </div>
      <Block>
        <DataGrid
          defaultPageSize={DEFAULT_PAGE_SIZE}
          totalItems={organization.members.totalItems}
          data={organization.members.items}
          fetchData={onChangePage}
          className="min-h-30"
        >
          <BaseColumn label={t("User")} id="user" minWidth={200}>
            {(membership) => <User user={membership.user} subtext />}
          </BaseColumn>
          <BaseColumn label={t("Organization Role")} id="org_role">
            {(member) => <OrganizationRoleBadge role={member.role} size="sm" />}
          </BaseColumn>
          <BaseColumn
            label={t("Workspace Roles")}
            id="workspace_roles"
            minWidth={300}
          >
            {(member) => (
              <WorkspaceRolesList
                workspaceMemberships={member.workspaceMemberships}
                size="sm"
                maxVisible={2}
              />
            )}
          </BaseColumn>
          <DateColumn
            className="py-4"
            accessor="createdAt"
            id="createdAt"
            label={t("Joined")}
            format={DateTime.DATE_FULL}
          />
          <BaseColumn className="flex justify-end gap-x-2">
            {(member) =>
              organization.permissions.manageMembers ? (
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
        </DataGrid>
      </Block>
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
