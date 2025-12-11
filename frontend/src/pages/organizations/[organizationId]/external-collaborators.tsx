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
import OrganizationExternalCollaborators from "organizations/features/OrganizationExternalCollaborators";

type Props = {
  organization: OrganizationQuery["organization"];
};

const OrganizationExternalCollaboratorsPage: NextPageWithLayout<Props> = ({
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
    <Page title={t("External Collaborators")}>
      <OrganizationLayout organization={organization}>
        <div className="p-6">
          <div className="m-8">
            <h1 className="text-4xl font-bold">{t("External Collaborators")}</h1>
            <p className="text-lg mt-2 text-gray-500">
              {t("Users with workspace access but no organization membership")}
            </p>
          </div>
          <div className="m-8">
            <OrganizationExternalCollaborators
              organizationId={organization.id}
            />
          </div>
        </div>
      </OrganizationLayout>
    </Page>
  );
};

OrganizationExternalCollaboratorsPage.getLayout = (page) => page;

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

export default OrganizationExternalCollaboratorsPage;
