import { gql } from "@apollo/client";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationsLayout from "./OrganizationsLayout";

type Props = {
  organizations: {
    id: string;
    name: string;
    workspaces: { items: { slug: string; name: string }[] };
  }[];
};

const ORGANIZATIONS_QUERY = gql`
  query Organizations {
    organizations {
      id
      name
      workspaces {
        items {
          slug
          name
        }
      }
    }
  }
`;

const OrganizationsPage: NextPageWithLayout<Props> = ({ organizations }) => {
  return <OrganizationsLayout organizations={organizations} />;
};

OrganizationsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await OrganizationsLayout.prefetch(ctx, client);
    const { data } = await client.query({
      query: ORGANIZATIONS_QUERY,
    });

    return {
      props: {
        organizations: data.organizations || [],
      },
    };
  },
});

export default OrganizationsPage;
