import { gql } from "@apollo/client";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "./OrganizationLayout";

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

// TODO : fix cookie set open
// TODO : clean UIs
// TODO : clean code

const OrganizationPage: NextPageWithLayout<Props> = ({ organization }) => {
  return (
    <OrganizationLayout organization={organization}>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">{organization.name}</h1>
        <ul>
          {organization.workspaces.items.map((workspace) => (
            <li key={workspace.slug} className="mb-2">
              <a
                href={`/workspaces/${workspace.slug}`}
                className="text-blue-600 hover:underline"
              >
                {workspace.name}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </OrganizationLayout>
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
