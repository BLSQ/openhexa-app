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

type Props = {
  organization: OrganizationQuery["organization"];
};

const OrganizationMembersPage: NextPageWithLayout<Props> = ({
  organization,
}) => {
  const { t } = useTranslation();

  if (!organization) {
    return null;
  }

  return (
    <Page title={t("Members")}>
      <OrganizationLayout organization={organization}>
        <div className="mx-auto max-w-6xl p-4">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">{t("Members")}</h1>
            <p className="mt-2 text-sm text-gray-600">
              {t("Manage organization members and send invitations")}
            </p>
          </div>
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
