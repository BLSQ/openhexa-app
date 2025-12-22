import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import useCacheKey from "core/hooks/useCacheKey";
import useDebounce from "core/hooks/useDebounce";
import SearchInput from "core/features/SearchInput";
import { DateTime } from "luxon";
import { useState, useEffect } from "react";
import { useTranslation } from "next-i18next";
// import DeleteOrganizationMemberDialog from "./DeleteOrganizationMemberDialog";
// import UpdateOrganizationMemberDialog from "./UpdateOrganizationMemberDialog";
import {
  useOrganizationExternalCollaboratorsQuery,
  OrganizationExternalCollaboratorsQuery,
} from "./OrganizationExternalCollaborators.generated";
import Block from "core/components/Block";
import User from "core/features/User";
import WorkspaceRolesList from "organizations/components/WorkspaceRolesList";
import useMe from "identity/hooks/useMe";

const DEFAULT_PAGE_SIZE = 10;

type ExternalCollaborator =
  OrganizationExternalCollaboratorsQuery["organization"]["externalCollaborators"]["items"][0];

export default function OrganizationExternalCollaborators({
  organizationId,
}: {
  organizationId: string;
}) {
  const { t } = useTranslation();
  const me = useMe();
  const [selectedCollaborator, setSelectedCollaborator] =
    useState<ExternalCollaborator>();
  // const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  // const [openEditDialog, setOpenEditDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [previousData, setPreviousData] =
    useState<OrganizationExternalCollaboratorsQuery | null>(null);

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const { data, refetch, loading } = useOrganizationExternalCollaboratorsQuery({
    variables: {
      id: organizationId,
      page: 1,
      perPage: DEFAULT_PAGE_SIZE,
      term: debouncedSearchTerm,
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
    }).then();
  };

  const displayData = data || previousData;
  const organization = displayData?.organization ?? {
    id: organizationId,
    externalCollaborators: { items: [], totalItems: 0 },
    permissions: { manageMembers: false, manageOwners: false },
    workspaces: { items: [] },
  };

  const handleDeleteClicked = (collaborator: ExternalCollaborator) => {
    setSelectedCollaborator(collaborator);
    // setOpenDeleteDialog(true);
  };

  const handleUpdateClicked = (collaborator: ExternalCollaborator) => {
    setSelectedCollaborator(collaborator);
    // setOpenEditDialog(true);
  };

  return (
    <>
      <div className="mb-4 flex gap-4">
        <SearchInput
          name="search-collaborators"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={t("Search external collaborators...")}
          loading={loading}
          className="max-w-md"
          fitWidth
        />
      </div>
      <Block>
        <DataGrid
          defaultPageSize={DEFAULT_PAGE_SIZE}
          totalItems={organization.externalCollaborators.totalItems}
          data={organization.externalCollaborators.items}
          fetchData={onChangePage}
          className="min-h-30"
        >
          <BaseColumn label={t("User")} id="user" minWidth={350}>
            {(collaborator) => <User user={collaborator.user} subtext />}
          </BaseColumn>
          <BaseColumn
            label={t("Workspace Roles")}
            id="workspace_roles"
            minWidth={300}
          >
            {(collaborator: ExternalCollaborator) => (
              <WorkspaceRolesList
                items={collaborator.workspaceMemberships}
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
            {(collaborator) => {
              const isCurrentUser = me?.user?.id === collaborator.user.id;
              const canManageMembers = organization.permissions.manageMembers;

              const canUpdateCollaborator = canManageMembers;
              const canDeleteCollaborator = canManageMembers && !isCurrentUser;

              return (
                <>
                  {canUpdateCollaborator && (
                    <Button
                      onClick={() => handleUpdateClicked(collaborator)}
                      size="sm"
                      variant="secondary"
                      aria-label="edit"
                    >
                      <PencilIcon className="h-4" />
                    </Button>
                  )}
                  {canDeleteCollaborator && (
                    <Button
                      onClick={() => handleDeleteClicked(collaborator)}
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
      {/* {selectedCollaborator && (
        <DeleteOrganizationMemberDialog
          open={openDeleteDialog}
          onClose={() => {
            setSelectedCollaborator(undefined);
            setOpenDeleteDialog(false);
          }}
          member={selectedCollaborator}
        />
      )}
      {selectedCollaborator && (
        <UpdateOrganizationMemberDialog
          open={openEditDialog}
          onClose={() => {
            setSelectedCollaborator(undefined);
            setOpenEditDialog(false);
          }}
          member={selectedCollaborator}
          organization={organization}
        />
      )} */}
    </>
  );
}
