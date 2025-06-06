import { gql } from "@apollo/client";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "./OrganizationLayout";
import { useTranslation } from "next-i18next";
import Page from "core/components/Page";
import Link from "core/components/Link";
import WorkspaceDisplay from "core/features/SpotlightSearch/WorkspaceDisplay";

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
          ...WorkspaceDisplayFragment
        }
      }
    }
  }
`;

const OrganizationPage: NextPageWithLayout<Props> = ({ organization }) => {
  const { t } = useTranslation();
  const totalWorkspaces = organization.workspaces.items.length;
  return (
    <Page title={t("Organization")}>
      <OrganizationLayout organization={organization}>
        <div className="p-6">
          <div className="m-8">
            <h1 className="text-4xl font-bold">{organization.name}</h1>
            <p className="text-lg mt-2 text-gray-500">
              {totalWorkspaces}{" "}
              {t(totalWorkspaces > 1 ? "workspaces" : "workspace")}
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {organization.workspaces.items.map((workspace) => (
              <div
                key={workspace.slug}
                className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300"
              >
                <WorkspaceDisplay workspace={{ name: "", countries: [] }} />
                <Link
                  href={`/workspaces/${workspace.slug}`}
                  className="text-blue-600 hover:text-blue-800 font-medium transition-colors mt-2 block"
                >
                  {t("View Workspace")}
                </Link>
              </div>
            ))}
          </div>
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
