import { gql } from "@apollo/client";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "./OrganizationLayout";
import { useTranslation } from "next-i18next";
import Page from "core/components/Page";
import Link from "core/components/Link";

type Props = {
  organization: {
    id: string;
    name: string;
    shortName?: string;
    workspaces: { items: { slug: string; name: string }[] };
  };
};

const ORGANIZATION_QUERY = gql`
  query Organization($id: UUID!) {
    organization(id: $id) {
      id
      name
      shortName
      workspaces {
        items {
          slug
          name
        }
      }
    }
  }
`;

// TODO : correct search
// TODO : clean UIs
// TODO : clean code

const OrganizationPage: NextPageWithLayout<Props> = ({ organization }) => {
  const { t } = useTranslation();
  return (
    <Page title={t("Organization")}>
      <OrganizationLayout organization={organization}>
        <div className="p-6">
          <h1 className="text-2xl font-bold mb-4">{organization.name}</h1>
          <ul>
            {organization.workspaces.items.map((workspace) => (
              <Link href={`/workspaces/${workspace.slug}`}>
                {workspace.name}
              </Link>
            ))}
          </ul>
        </div>
      </OrganizationLayout>
    </Page>
  );
};

OrganizationPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await OrganizationLayout.prefetch(ctx, client);
    const { data } = await client.query({
      query: ORGANIZATION_QUERY,
      variables: { id: ctx.params?.organizationId },
    });

    if (!data.organization) {
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

export default OrganizationPage;
