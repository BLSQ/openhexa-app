import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import useCacheKey from "core/hooks/useCacheKey";
import useDebounce from "core/hooks/useDebounce";
import SearchInput from "core/features/SearchInput";
import Listbox from "core/components/Listbox";
import {
  User as UserType,
  OrganizationMembership,
  OrganizationMembershipRole,
} from "graphql/types";
import { DateTime } from "luxon";
import { useState, useEffect } from "react";
import { useTranslation } from "next-i18next";
import DeleteOrganizationMemberDialog from "./DeleteOrganizationMemberDialog";
import UpdateOrganizationMemberDialog from "./UpdateOrganizationMemberDialog";
import {
  OrganizationMembersQuery,
} from "./OrganizationMembers.generated";
import Block from "core/components/Block";
import User from "core/features/User";
import OrganizationRoleBadge from "organizations/components/OrganizationRoleBadge";
import WorkspaceRolesList from "organizations/components/WorkspaceRolesList";
import useMe from "identity/hooks/useMe";
import { formatOrganizationMembershipRole } from "organizations/helpers/organization";
import { useQuery } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const OrganizationMembersDoc = graphql(`
query OrganizationMembers($id: UUID!, $page: Int, $perPage: Int, $term: String, $role: OrganizationMembershipRole) {
  organization(id: $id) {
    id
    permissions {
      manageMembers
      manageOwners
    }
    workspaces(perPage: 1000, page: 1) {
      items {
        slug
        name
      }
    }
    members(page: $page, perPage: $perPage, term: $term, role: $role) {
      totalItems
      items {
        id
        role
        workspaceMemberships {
          ...WorkspaceRole
          id
          role
          workspace {
            slug
            name
          }
        }
        user {
          ...User_user
        }
        createdAt
      }
    }
  }
}
`);

const DEFAULT_PAGE_SIZE = 10;

const ALL_ROLES = "ALL_ROLES";
type RoleFilterOption = OrganizationMembershipRole | typeof ALL_ROLES;
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
  const { t } = useTranslation();
  const me = useMe();
  const [selectedMember, setSelectedMember] = useState<OrganizationMember>();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState<RoleFilterOption>(ALL_ROLES);
  const [previousData, setPreviousData] =
    useState<OrganizationMembersQuery | null>(null);

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const { data, refetch, loading } = useQuery(OrganizationMembersDoc, {
    variables: {
      id: organizationId,
      page: 1,
      perPage: DEFAULT_PAGE_SIZE,
      term: debouncedSearchTerm,
      role: roleFilter === ALL_ROLES ? undefined : roleFilter,
    },
    fetchPolicy: "cache-and-network",
    notifyOnNetworkStatusChange: true,
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
      role: roleFilter === ALL_ROLES ? undefined : roleFilter,
    }).then();
  };

  const displayData = data || previousData;
  const organization = displayData?.organization ?? {
    id: organizationId,
    members: { items: [], totalItems: 0 },
    permissions: { manageMembers: false, manageOwners: false },
    workspaces: { items: [] },
  };

  const handleDeleteClicked = (member: OrganizationMember) => {
    setSelectedMember(member);
    setOpenDeleteDialog(true);
  };

  const handleUpdateClicked = (member: OrganizationMember) => {
    setSelectedMember(member);
    setOpenEditDialog(true);
  };

  const roleOptions = [
    { value: ALL_ROLES, label: t("All roles") },
    ...Object.values(OrganizationMembershipRole).map((role) => ({
      value: role,
      label: formatOrganizationMembershipRole(role),
    })),
  ];

  return (
    <>
      <div className="mb-4 flex gap-4">
        <SearchInput
          name="search-members"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={t("Search members...")}
          loading={loading}
          className="max-w-md"
          fitWidth
        />
        <div className="w-30">
          <Listbox
            value={
              roleOptions.find((opt) => opt.value === roleFilter) ||
              roleOptions[0]
            }
            options={roleOptions}
            onChange={(option) => setRoleFilter(option.value)}
            getOptionLabel={(opt) => opt.label}
            by="value"
          />
        </div>
      </div>
      <Block>
        <DataGrid
          defaultPageSize={DEFAULT_PAGE_SIZE}
          totalItems={organization.members.totalItems}
          data={organization.members.items}
          fetchData={onChangePage}
          className="min-h-30"
        >
          <BaseColumn label={t("User")} id="user" minWidth={350}>
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
            {(member: OrganizationMember) => (
              <WorkspaceRolesList
                items={member.workspaceMemberships}
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
            {(member) => {
              const isCurrentUser = me?.user?.id === member.user.id;
              const isOwner = member.role === OrganizationMembershipRole.Owner;
              const canManageOwners = organization.permissions.manageOwners;
              const canManageMembers = organization.permissions.manageMembers;

              const canUpdateMember =
                canManageMembers && (!isOwner || canManageOwners);
              const canDeleteMember = canUpdateMember && !isCurrentUser;

              return (
                <>
                  {canUpdateMember && (
                    <Button
                      onClick={() => handleUpdateClicked(member)}
                      size="sm"
                      variant="secondary"
                      aria-label="edit"
                    >
                      <PencilIcon className="h-4" />
                    </Button>
                  )}
                  {canDeleteMember && (
                    <Button
                      onClick={() => handleDeleteClicked(member)}
                      size="sm"
                      variant="secondary"
                      aria-label="delete"
                    >
                      <TrashIcon className="h-4" />
                    </Button>
                  )}
                </>
              );
            }}
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
          organization={organization}
        />
      )}
    </>
  );
}
