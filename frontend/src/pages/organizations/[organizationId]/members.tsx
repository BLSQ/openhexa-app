import { useTranslation } from "next-i18next";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "organizations/layouts/OrganizationLayout";
import {
  OrganizationDocument,
  OrganizationQuery,
} from "organizations/graphql/queries.generated";
import Page from "core/components/Page";
import Button from "core/components/Button";
import { PlusIcon } from "@heroicons/react/24/outline";
import OrganizationMembers from "organizations/features/OrganizationMembers";
import AddOrganizationMemberDialog from "organizations/features/OrganizationMembers/AddOrganizationMemberDialog";
import { useState } from "react";
import OrganizationInvitations from "organizations/features/OrganizationInvitations";
import Title from "core/components/Title";

type Props = {
  organization: OrganizationQuery["organization"];
};

// TODO : sidebar overlay transition and tooltips
// TODO : handle existing user when inviting + resending invitation
// TODO : fe for invitations (changing roles, prevent overriding)
// TODO : update
// TODO : delete
// TODO : prevent adding existing members
// TODO : permissions on actions from the backend
// TODO : tests

const OrganizationMembersPage: NextPageWithLayout<Props> = ({
  organization,
}) => {
  const [isNewMemberDialogOpen, setIsNewMemberDialogOpen] = useState(false);

  const { t } = useTranslation();

  if (!organization) {
    return null;
  }

  return (
    <Page title={t("Members")}>
      <OrganizationLayout organization={organization}>
        <div className="p-6">
          <div className="m-8 flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold">{t("Members")}</h1>
              <p className="text-lg mt-2 text-gray-500">
                {organization.members.totalItems}{" "}
                {organization.members.totalItems > 1
                  ? t("members")
                  : t("member")}
              </p>
            </div>
            <Button
              variant="primary"
              className="static"
              onClick={() => setIsNewMemberDialogOpen(true)}
              leadingIcon={<PlusIcon className="w-4" />}
              disabled={!organization.permissions.manageMembers}
            >
              {t("Invite member")}
            </Button>
          </div>
          <div className="m-8">
            <OrganizationMembers organizationId={organization.id} />
          </div>
          <div className="m-8">
            <Title level={2}>{t("Pending invitations")}</Title>
            <OrganizationInvitations organizationId={organization.id} />
          </div>
        </div>
        <AddOrganizationMemberDialog
          open={isNewMemberDialogOpen}
          onClose={() => setIsNewMemberDialogOpen(false)}
          organizationId={organization.id}
        />
      </OrganizationLayout>
    </Page>
  );
};

OrganizationMembersPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await OrganizationLayout.prefetch(ctx);
    const { data } = await client.query({
      query: OrganizationDocument,
      variables: {
        id: ctx.params?.organizationId as string,
      },
    });

    if (!data?.organization) {
      return {
        notFound: true,
      };
    }

    return {
      props: {
        organization: data.organization,
      },
    };
  },
});

export default OrganizationMembersPage;
