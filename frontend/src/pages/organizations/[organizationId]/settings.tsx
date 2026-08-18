import { useTranslation } from "next-i18next";
import { isValidUuid } from "core/helpers";
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
import OrganizationAiSettings from "organizations/features/OrganizationAiSettings";
import OrganizationUsageLimits from "organizations/features/OrganizationUsageLimits";

type Props = {
  organization: OrganizationQuery["organization"];
};

const OrganizationSettingsPage: NextPageWithLayout<Props> = ({
  organization: SSROrganization,
}) => {
  const { t } = useTranslation();

  const { data: clientOrganization } = useOrganizationQuery({
    variables: { id: SSROrganization?.id },
    skip: !SSROrganization?.id,
  });

  const organization = clientOrganization?.organization || SSROrganization;

  if (!organization) {
    return null;
  }

  // Only admins and owners can access settings
  if (!organization.permissions.update) {
    return null;
  }

  return (
    <Page title={t("Settings")}>
      <OrganizationLayout
        organization={organization}
        header={
          <div>
            <h1 className="text-xl font-bold">{t("Organization Settings")}</h1>
          </div>
        }
      >
        <OrganizationSettings organization={organization} />
        <OrganizationAiSettings organization={organization} />
        <OrganizationUsageLimits organization={organization} />
      </OrganizationLayout>
    </Page>
  );
};

OrganizationSettingsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const organizationId = ctx.params?.organizationId;
    if (!isValidUuid(organizationId)) {
      return {
        notFound: true,
      };
    }

    await OrganizationLayout.prefetch(ctx);
    const { data } = await client.query({
      query: OrganizationDocument,
      variables: {
        id: organizationId,
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

export default OrganizationSettingsPage;
