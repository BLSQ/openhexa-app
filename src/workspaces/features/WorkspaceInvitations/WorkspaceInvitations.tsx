import { gql, useQuery } from "@apollo/client";
import DataGrid from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import useCacheKey from "core/hooks/useCacheKey";
import { capitalize } from "lodash";
import { DateTime } from "luxon";
import { useTranslation } from "react-i18next";
import { WorskspaceInvitationsQuery } from "./WorkspaceInvitations.generated";
import { WorkspaceInvitationStatus } from "graphql-types";

const DEFAULT_PAGE_SIZE = 5;

export default function WorkspaceInvitations({
  workspaceSlug,
}: {
  workspaceSlug: string;
}) {
  const { t } = useTranslation();

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
          invitations(status: $status, page: $page, perPage: $perPage) {
            totalItems
            items {
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
    }
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

  return (
    <>
      <DataGrid
        className="bg-white shadow-md"
        defaultPageSize={DEFAULT_PAGE_SIZE}
        totalItems={workspace.invitations.totalItems}
        fixedLayout={false}
        data={workspace.invitations.items}
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
      </DataGrid>
    </>
  );
}
