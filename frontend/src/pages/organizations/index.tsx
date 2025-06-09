import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationsLayout from "organizations/layouts/OrganizationsLayout";
import { useTranslation } from "next-i18next";
import Page from "core/components/Page";
import {
  OrganizationsDocument,
  OrganizationsQuery,
} from "organizations/graphql/queries.generated";

type Props = {
  organizations: OrganizationsQuery["organizations"];
};

const OrganizationsPage: NextPageWithLayout<Props> = ({ organizations }) => {
  const { t } = useTranslation();
  return (
    <Page title={t("Organizations")}>
      <OrganizationsLayout organizations={organizations} />
    </Page>
  );
};

OrganizationsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await OrganizationsLayout.prefetch(ctx);
    const { data } = await client.query({
      query: OrganizationsDocument,
    });

    return {
      props: {
        organizations: data.organizations || [],
      },
    };
  },
});

export default OrganizationsPage;
