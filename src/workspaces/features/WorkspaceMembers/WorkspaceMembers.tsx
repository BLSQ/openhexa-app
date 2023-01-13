import { gql, useQuery } from "@apollo/client";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import useCacheKey from "core/hooks/useCacheKey";
import { capitalize } from "lodash";
import { DateTime } from "luxon";
import { useTranslation } from "react-i18next";
import { WorskspaceMembersQuery } from "./WorkspaceMembers.generated";

const DEFAULT_PAGE_SIZE = 5;

export default function WorkspaceMembers({
  workspaceId,
}: {
  workspaceId: string;
}) {
  const { t } = useTranslation();
  const { data, refetch } = useQuery<WorskspaceMembersQuery>(
    gql`
      query WorskspaceMembers($id: String!, $page: Int, $perPage: Int) {
        workspace(id: $id) {
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
    { variables: { id: workspaceId, page: 1, perPage: DEFAULT_PAGE_SIZE } }
  );

  useCacheKey("workspace", () => refetch());

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      page,
      id: workspaceId,
    });
  };

  if (!data?.workspace) {
    return null;
  }

  const { workspace } = data;

  return (
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
        label="Name"
        defaultValue="-"
      />
      <TextColumn
        className="max-w-[50ch] py-3 "
        accessor={({ user }) => user.email}
        id="email"
        label="Email"
      />
      <TextColumn
        className="max-w-[50ch] py-3 "
        accessor={(member) => capitalize(member.role)}
        label="Role"
        id="member_role"
      />
      <DateColumn
        className="max-w-[50ch] py-3 "
        accessor="createdAt"
        id="createdAt"
        label="Joined"
        format={DateTime.DATE_FULL}
      />
      <BaseColumn>
        {() => (
          <Button size="sm" variant="secondary">
            {t("Edit")}
          </Button>
        )}
      </BaseColumn>
    </DataGrid>
  );
}
