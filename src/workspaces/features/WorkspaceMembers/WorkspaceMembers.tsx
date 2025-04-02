import { gql, useQuery } from "@apollo/client";
import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import useCacheKey from "core/hooks/useCacheKey";
import { User, WorkspaceMembership } from "graphql/types";
import { DateTime } from "luxon";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import DeleteWorkspaceMemberDialog from "./DeleteWorkspaceMemberDialog";
import UpdateWorkspaceMemberDialog from "./UpdateWorkspaceMemberDialog";
import { WorskspaceMembersQuery } from "./WorkspaceMembers.generated";
import useMe from "identity/hooks/useMe";
import { formatWorkspaceMembershipRole } from "workspaces/helpers/workspace";

const DEFAULT_PAGE_SIZE = 10;

type WorkspaceMember = Pick<WorkspaceMembership, "id" | "role"> & {
  user: Pick<User, "id" | "displayName">;
};

export default function WorkspaceMembers({
  workspaceSlug,
}: {
  workspaceSlug: string;
}) {
  const me = useMe();
  const { t } = useTranslation();
  const [selectedMember, setSelectedMember] = useState<WorkspaceMember>();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);

  const { data, refetch } = useQuery<WorskspaceMembersQuery>(
    gql`
      query WorskspaceMembers($slug: String!, $page: Int, $perPage: Int) {
        workspace(slug: $slug) {
          slug
          permissions {
            manageMembers
          }
          members(page: $page, perPage: $perPage) {
            totalItems
            items {
              id
              role
              user {
                id
                displayName
                email
              }
              createdAt
            }
          }
        }
      }
    `,
    { variables: { slug: workspaceSlug, page: 1, perPage: DEFAULT_PAGE_SIZE } },
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

  const { workspace } = data;

  const handleDeleteClicked = (memberId: string) => {
    const member = workspace.members.items.filter((m) => m.id === memberId)[0];
    setSelectedMember(member);
    setOpenDeleteDialog(true);
  };

  const handleUpdateClicked = (memberId: string) => {
    const member = workspace.members.items.filter((m) => m.id === memberId)[0];
    setSelectedMember(member);
    setOpenEditDialog(true);
  };

  return (
    <>
      <DataGrid
        className="bg-white shadow-md"
        defaultPageSize={DEFAULT_PAGE_SIZE}
        totalItems={workspace.members.totalItems}
        fixedLayout={false}
        data={workspace.members.items}
        fetchData={onChangePage}
      >
        <TextColumn
          className="max-w-[50ch] py-3 "
          accessor={({ user }) => user.displayName}
          id="name"
          label={t("Name")}
          defaultValue="-"
        />
        <TextColumn
          className="max-w-[50ch] py-3 "
          accessor={({ user }) => user.email}
          id="email"
          label={t("Email")}
        />
        <TextColumn
          className="max-w-[50ch] py-3 "
          accessor={(member) => formatWorkspaceMembershipRole(member.role)}
          label={t("Role")}
          id="member_role"
        />
        <DateColumn
          className="max-w-[50ch] py-3 "
          accessor="createdAt"
          id="createdAt"
          label={t("Joined")}
          format={DateTime.DATE_FULL}
        />
        {workspace.permissions.manageMembers && (
          <BaseColumn className="flex justify-end gap-x-2">
            {(member) =>
              me.user?.id !== member.user.id ? (
                <>
                  <Button
                    onClick={() => handleUpdateClicked(member.id)}
                    size="sm"
                    variant="secondary"
                  >
                    <PencilIcon className="h-4" />
                  </Button>
                  <Button
                    onClick={() => handleDeleteClicked(member.id)}
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
        <DeleteWorkspaceMemberDialog
          open={openDeleteDialog}
          onClose={() => {
            setSelectedMember(undefined);
            setOpenDeleteDialog(false);
          }}
          member={selectedMember}
        />
      )}
      {selectedMember && (
        <UpdateWorkspaceMemberDialog
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
