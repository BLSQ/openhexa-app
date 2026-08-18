import { useTranslation } from "next-i18next";
import { isValidUuid } from "core/helpers";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "organizations/layouts/OrganizationLayout";
import {
  OrganizationDatasetsDocument,
  OrganizationDatasetsQuery,
} from "organizations/graphql/queries.generated";
import Page from "core/components/Page";
import OrganizationDatasets from "organizations/features/OrganizationDatasets";

type Props = {
  organization: OrganizationDatasetsQuery["organization"];
};

const OrganizationDatasetsPage: NextPageWithLayout<Props> = ({
  organization,
}) => {
  const { t } = useTranslation();

  if (!organization) {
    return null;
  }

  const totalDatasets = organization.datasetLinks?.totalItems ?? 0;

  return (
    <Page title={t("Datasets")}>
      <OrganizationLayout
        organization={organization}
        header={
          <div>
            <h1 className="text-2xl font-bold">{t("Datasets")}</h1>
            <p className="text-sm text-gray-500">
              {totalDatasets} {totalDatasets > 1 ? t("Datasets") : t("Dataset")}
            </p>
          </div>
        }
      >
        <OrganizationDatasets organization={organization} />
      </OrganizationLayout>
    </Page>
  );
};

OrganizationDatasetsPage.getLayout = (page) => page;

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
      query: OrganizationDatasetsDocument,
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

export default OrganizationDatasetsPage;
