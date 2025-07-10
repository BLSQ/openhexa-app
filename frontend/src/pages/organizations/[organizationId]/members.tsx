import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "organizations/layouts/OrganizationLayout";
import {
  OrganizationDocument,
  OrganizationQuery,
} from "organizations/graphql/queries.generated";
import Page from "core/components/Page";
import Title from "../../../core/components/Title";
import Button from "../../../core/components/Button";
import { PlusCircleIcon } from "@heroicons/react/24/outline";
import WorkspaceMembers from "../../../workspaces/features/WorkspaceMembers";
import { useState } from "react";
import Block from "../../../core/components/Block";

type Props = {
  organization: OrganizationQuery["organization"];
};

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
          <div>
            <h1 className="text-4xl font-bold m-8">{t("Members")}</h1>
          </div>
        </div>
        <div className="m-8 flex justify-end">
          <Button
            onClick={() => setIsNewMemberDialogOpen(true)}
            leadingIcon={<PlusCircleIcon className="mr-1 h-4 w-4" />}
          >
            {t("Add/Invite member")}
          </Button>
        </div>
        <div className="m-8">
          <Block>
            <WorkspaceMembers workspaceSlug={"test"} />
          </Block>
        </div>
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
