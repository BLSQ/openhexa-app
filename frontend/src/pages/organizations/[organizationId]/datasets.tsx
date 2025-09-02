import { useTranslation } from "next-i18next";
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

  return (
    <Page title={t("Datasets")}>
      <OrganizationLayout organization={organization}>
        <div className="p-6">
          <div className="m-8 flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold">{t("Datasets")}</h1>
              <p className="text-lg mt-2 text-gray-500">
                {t("All datasets available in this organization")}
              </p>
            </div>
          </div>
          <div className="m-8">
            <OrganizationDatasets
              organizationId={organization.id}
              datasets={organization.datasets}
            />
          </div>
        </div>
      </OrganizationLayout>
    </Page>
  );
};

OrganizationDatasetsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await OrganizationLayout.prefetch(ctx);
    const { data } = await client.query({
      query: OrganizationDatasetsDocument,
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

export default OrganizationDatasetsPage;
