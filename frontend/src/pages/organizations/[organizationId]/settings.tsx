import { useTranslation } from "next-i18next";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "organizations/layouts/OrganizationLayout";
import {
  OrganizationDocument,
  OrganizationQuery,
  useOrganizationQuery,
} from "organizations/graphql/queries.generated";
import Page from "core/components/Page";
import OrganizationSettings from "organizations/features/OrganizationSettings";

type Props = {
  organization: OrganizationQuery["organization"];
};

const OrganizationSettingsPage: NextPageWithLayout<Props> = ({
  organization: SRROrganization,
}) => {
  const { t } = useTranslation();

  const { data: clientOrganization } = useOrganizationQuery({
    variables: { id: SRROrganization?.id },
    skip: !SRROrganization?.id,
  });

  const organization = clientOrganization?.organization || SRROrganization;

  if (!organization) {
    return null;
  }

  return (
    <Page title={t("Settings")}>
      <OrganizationLayout organization={organization}>
        <div className="p-6">
          <div className="m-8">
            <h1 className="text-4xl font-bold">{t("Settings")}</h1>
            <p className="text-lg mt-2 text-gray-500">
              {t("Manage your organization settings")}
            </p>
          </div>
          <div className="m-8">
            <OrganizationSettings organization={organization} />
          </div>
        </div>
      </OrganizationLayout>
    </Page>
  );
};

OrganizationSettingsPage.getLayout = (page) => page;

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

    if (!data.organization.permissions.updateSettings) {
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

export default OrganizationSettingsPage;
